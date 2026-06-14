"""Problem registry for the interview lab.

Problems are defined here as data. A problem drives the prompt shown to the
candidate, the starter code in the editor, and how a submission is graded.
Two languages are supported:

- ``python``: the candidate defines a function; the sandbox calls it with each
  test case's input and compares the return value to the expected output.
- ``sql``: the candidate writes a query; the sandbox runs it against a fresh
  in-memory SQLite database seeded with ``setup_sql`` and compares the result
  rows to ``expected_rows``.

Grading itself always happens inside the sandbox (see ``sandbox.py``). This
module only holds specifications. ``list_problems()`` deliberately omits the
grading data (test cases / expected rows) so the answer is never sent to the
client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass(frozen=True)
class TestCase:
    """A single Python test case: call the entrypoint with ``input`` (kwargs)
    and expect ``expected`` back. ``unordered`` compares lists as collections."""

    input: Dict[str, Any]
    expected: Any
    description: str = ""
    unordered: bool = False


@dataclass(frozen=True)
class PythonProblem:
    id: str
    title: str
    prompt: str
    starter_code: str
    entrypoints: List[str]  # accepted function names, first defined match wins
    test_cases: List[TestCase]
    language: str = "python"


@dataclass(frozen=True)
class SqlProblem:
    id: str
    title: str
    prompt: str
    starter_code: str
    setup_sql: str  # schema + seed data, run before the candidate's query
    expected_columns: List[str]
    expected_rows: List[List[Any]]
    order_matters: bool = True
    language: str = "sql"


Problem = Union[PythonProblem, SqlProblem]


_TWO_SUM = PythonProblem(
    id="two-sum",
    title="Two Sum",
    prompt=(
        "Given an array of integers `nums` and an integer `target`, return the "
        "indices of the two numbers that add up to `target`. Assume each input "
        "has exactly one solution and you may not use the same element twice. "
        "Define a function `two_sum(nums, target)` (or `twoSum`)."
    ),
    starter_code=(
        "def two_sum(nums, target):\n"
        "    # TODO: return indices of the two numbers that add up to target\n"
        "    pass\n"
    ),
    entrypoints=["two_sum", "twoSum"],
    test_cases=[
        TestCase(
            input={"nums": [2, 7, 11, 15], "target": 9},
            expected=[0, 1],
            description="Solution at the beginning",
            unordered=True,
        ),
        TestCase(
            input={"nums": [3, 2, 4], "target": 6},
            expected=[1, 2],
            description="Solution in the middle",
            unordered=True,
        ),
        TestCase(
            input={"nums": [3, 3], "target": 6},
            expected=[0, 1],
            description="Duplicate values",
            unordered=True,
        ),
    ],
)


_HIGH_EARNERS = SqlProblem(
    id="high-earners",
    title="High Earners",
    prompt=(
        "An `employees` table holds `id`, `name`, `department`, and `salary`. "
        "Write a query that returns the `name` and `salary` of every employee "
        "earning **more than 50000**, ordered by `salary` from highest to "
        "lowest."
    ),
    starter_code=(
        "-- Return name and salary of employees earning more than 50000,\n"
        "-- highest salary first.\n"
        "SELECT name, salary\n"
        "FROM employees\n"
        ";\n"
    ),
    setup_sql=(
        "CREATE TABLE employees (\n"
        "    id INTEGER PRIMARY KEY,\n"
        "    name TEXT NOT NULL,\n"
        "    department TEXT NOT NULL,\n"
        "    salary INTEGER NOT NULL\n"
        ");\n"
        "INSERT INTO employees (id, name, department, salary) VALUES\n"
        "    (1, 'Alice', 'Engineering', 85000),\n"
        "    (2, 'Bob',   'Sales',       45000),\n"
        "    (3, 'Carol', 'Engineering', 72000),\n"
        "    (4, 'Dave',  'Marketing',   50000),\n"
        "    (5, 'Eve',   'Sales',       95000),\n"
        "    (6, 'Frank', 'Marketing',   48000);\n"
    ),
    expected_columns=["name", "salary"],
    # salary > 50000, ordered desc. Dave (exactly 50000) is excluded.
    expected_rows=[
        ["Eve", 95000],
        ["Alice", 85000],
        ["Carol", 72000],
    ],
    order_matters=True,
)


# Insertion order is preserved and reflected in the UI problem picker.
_PROBLEMS: Dict[str, Problem] = {
    _TWO_SUM.id: _TWO_SUM,
    _HIGH_EARNERS.id: _HIGH_EARNERS,
}


def get_problem(problem_id: str) -> Problem | None:
    """Return the full problem (including grading data) or ``None``."""
    return _PROBLEMS.get(problem_id)


def list_problems() -> List[Dict[str, str]]:
    """Public, answer-free summaries for the client."""
    return [
        {
            "id": p.id,
            "title": p.title,
            "language": p.language,
            "prompt": p.prompt,
            "starter_code": p.starter_code,
        }
        for p in _PROBLEMS.values()
    ]
