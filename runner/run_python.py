"""Sandbox runner for Python submissions.

Runs INSIDE the executor container (never imported by the API process). Reads a
JSON job from stdin, executes the candidate's code, grades it against the test
cases, and writes a single JSON result line to stdout.

Job shape:
    {"code": str, "entrypoints": [str], "test_cases": [{"input": {...},
     "expected": Any, "unordered": bool, "description": str}]}

Result shape:
    {"status": "completed"|"error", "output": str, "error": str|None,
     "test_results": [bool], "test_passed": int, "test_total": int}
"""

import contextlib
import io
import json
import sys


def _matches(got, expected, unordered):
    if unordered and isinstance(got, list) and isinstance(expected, list):
        try:
            return sorted(got) == sorted(expected)
        except TypeError:
            return got == expected
    return got == expected


def main():
    job = json.load(sys.stdin)
    code = job["code"]
    entrypoints = job.get("entrypoints", [])
    test_cases = job.get("test_cases", [])

    result = {
        "status": "completed",
        "output": "",
        "error": None,
        "test_results": [False] * len(test_cases),
        "test_passed": 0,
        "test_total": len(test_cases),
    }

    stdout_buf = io.StringIO()
    namespace = {}

    # Define the candidate's function(s).
    try:
        with contextlib.redirect_stdout(stdout_buf):
            exec(code, namespace)
    except Exception as exc:  # noqa: BLE001 - report any candidate error
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["output"] = stdout_buf.getvalue()
        print(json.dumps(result))
        return

    func = None
    for name in entrypoints:
        candidate = namespace.get(name)
        if callable(candidate):
            func = candidate
            break

    if func is None:
        result["status"] = "error"
        result["error"] = "No function named " + " or ".join(
            f"'{n}'" for n in entrypoints
        ) + " was defined."
        result["output"] = stdout_buf.getvalue()
        print(json.dumps(result))
        return

    for i, case in enumerate(test_cases):
        try:
            with contextlib.redirect_stdout(stdout_buf):
                got = func(**case["input"])
            if _matches(got, case["expected"], case.get("unordered", False)):
                result["test_results"][i] = True
        except Exception:  # noqa: BLE001 - a failing test is not a hard error
            result["test_results"][i] = False

    result["test_passed"] = sum(result["test_results"])
    result["output"] = stdout_buf.getvalue()
    print(json.dumps(result))


if __name__ == "__main__":
    main()
