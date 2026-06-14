"""Executes untrusted candidate submissions in an isolated sandbox.

Primary path: an ephemeral, hardened Docker container (one per submission),
launched via the docker CLI. The candidate code + problem spec are passed on
stdin as JSON; a runner script inside the container executes and grades it and
writes a JSON result line to stdout.

If Docker is unavailable we FAIL CLOSED -- untrusted code is never run on the
host -- unless ``ALLOW_UNSANDBOXED=1`` is set, an explicit dev-only escape hatch
that runs the same runner scripts via the host interpreter (no isolation).
"""

import json
import os
import shutil
import subprocess
import sys
import time

import problems

EXECUTOR_IMAGE = os.getenv("EXECUTOR_IMAGE", "interview-executor")
RUN_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "10"))
ALLOW_UNSANDBOXED = os.getenv("ALLOW_UNSANDBOXED") == "1"

_RUNNERS = {"python": "run_python.py", "sql": "run_sql.py"}
_RUNNER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runner")


def _docker_available() -> bool:
    docker_bin = shutil.which("docker")
    if not docker_bin:
        return False
    try:
        proc = subprocess.run(
            [docker_bin, "version"], capture_output=True, timeout=5
        )
        return proc.returncode == 0
    except Exception:
        return False


DOCKER_AVAILABLE = _docker_available()


def sandbox_mode() -> str:
    if DOCKER_AVAILABLE:
        return "docker"
    if ALLOW_UNSANDBOXED:
        return "host-unsandboxed"
    return "unavailable"


def _build_job(problem, code: str) -> dict:
    if problem.language == "python":
        return {
            "code": code,
            "entrypoints": problem.entrypoints,
            "test_cases": [
                {
                    "input": tc.input,
                    "expected": tc.expected,
                    "unordered": tc.unordered,
                    "description": tc.description,
                }
                for tc in problem.test_cases
            ],
        }
    # sql
    return {
        "query": code,
        "setup_sql": problem.setup_sql,
        "expected_rows": problem.expected_rows,
        "order_matters": problem.order_matters,
    }


def run(problem, code: str) -> dict:
    """Run + grade a submission. Returns the runner's result dict, augmented
    with ``runtime``. On infrastructure failure returns a dict carrying
    ``sandbox_unavailable: True`` (the API turns that into a 503)."""
    runner = _RUNNERS[problem.language]
    job = json.dumps(_build_job(problem, code))
    start = time.time()

    if DOCKER_AVAILABLE:
        result = _run_in_docker(runner, job)
    elif ALLOW_UNSANDBOXED:
        result = _run_on_host(runner, job)
    else:
        return {
            "status": "error",
            "output": "",
            "error": (
                "Sandbox unavailable: Docker is required to run submissions. "
                "Set ALLOW_UNSANDBOXED=1 to run on the host for local dev."
            ),
            "sandbox_unavailable": True,
        }

    result.setdefault("runtime", round(time.time() - start, 4))
    return result


def _run_in_docker(runner: str, job: str) -> dict:
    cmd = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", "256m",
        "--cpus", "0.5",
        "--pids-limit", "64",
        "--read-only",
        "--tmpfs", "/tmp:size=16m",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--user", "nobody",
        EXECUTOR_IMAGE,
        # Self-terminate inside the container as well as via the host timeout.
        "timeout", str(RUN_TIMEOUT), "python", f"/app/{runner}",
    ]
    # Allow extra wall-clock for image start / cleanup beyond the inner timeout.
    return _invoke(cmd, job, wall_timeout=RUN_TIMEOUT + 15)


def _run_on_host(runner: str, job: str) -> dict:
    cmd = [sys.executable, os.path.join(_RUNNER_DIR, runner)]
    return _invoke(cmd, job, wall_timeout=RUN_TIMEOUT)


def _invoke(cmd, job: str, wall_timeout: int) -> dict:
    try:
        proc = subprocess.run(
            cmd, input=job, capture_output=True, text=True, timeout=wall_timeout
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "output": "",
            "error": f"Execution timed out ({RUN_TIMEOUT}s limit).",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "output": "",
            "error": f"Sandbox error: {exc}",
        }

    # 124 is the exit code GNU `timeout` uses when it kills the process.
    if proc.returncode == 124:
        return {
            "status": "error",
            "output": "",
            "error": f"Execution timed out ({RUN_TIMEOUT}s limit).",
        }

    stdout = (proc.stdout or "").strip()
    if not stdout:
        return {
            "status": "error",
            "output": "",
            "error": (proc.stderr or "").strip()
            or f"Sandbox produced no output (exit code {proc.returncode}).",
        }

    try:
        # The runner prints one JSON line; tolerate stray prior output.
        return json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError:
        return {
            "status": "error",
            "output": stdout,
            "error": "Could not parse sandbox result."
            + (f" stderr: {proc.stderr.strip()}" if proc.stderr else ""),
        }
