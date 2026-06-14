"""Sandbox runner for SQL submissions.

Runs INSIDE the executor container (never imported by the API process). Reads a
JSON job from stdin, runs the candidate query against a fresh in-memory SQLite
database seeded with ``setup_sql``, compares the result set to ``expected_rows``,
and writes a single JSON result line to stdout.

Job shape:
    {"query": str, "setup_sql": str, "expected_rows": [[...]],
     "order_matters": bool}

Result shape matches run_python.py (test_total is always 1 for SQL).
"""

import json
import sqlite3
import sys


def _row_key(row):
    # Stable ordering for set-style comparison across heterogeneous types.
    return tuple(str(c) for c in row)


def _render(columns, rows):
    if not rows:
        return "(no rows)"
    lines = []
    if columns:
        lines.append(" | ".join(str(c) for c in columns))
        lines.append("-" * len(lines[0]))
    for row in rows:
        lines.append(" | ".join("NULL" if c is None else str(c) for c in row))
    return "\n".join(lines)


def main():
    job = json.load(sys.stdin)
    query = job["query"]
    setup_sql = job.get("setup_sql", "")
    expected_rows = [list(r) for r in job.get("expected_rows", [])]
    order_matters = job.get("order_matters", True)

    result = {
        "status": "completed",
        "output": "",
        "error": None,
        "test_results": [False],
        "test_passed": 0,
        "test_total": 1,
    }

    conn = sqlite3.connect(":memory:")
    try:
        try:
            conn.executescript(setup_sql)
        except Exception as exc:  # noqa: BLE001
            result["status"] = "error"
            result["error"] = f"Failed to set up the problem schema: {exc}"
            print(json.dumps(result))
            return

        try:
            cursor = conn.execute(query)
            columns = [d[0] for d in cursor.description] if cursor.description else []
            rows = [list(r) for r in cursor.fetchall()]
        except Exception as exc:  # noqa: BLE001 - report candidate query error
            result["status"] = "error"
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(json.dumps(result))
            return
    finally:
        conn.close()

    if order_matters:
        passed = rows == expected_rows
    else:
        passed = sorted(rows, key=_row_key) == sorted(expected_rows, key=_row_key)

    result["test_results"] = [passed]
    result["test_passed"] = 1 if passed else 0
    result["output"] = _render(columns, rows)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
