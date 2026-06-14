from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    problem_id: str
    code: str


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: Optional[str] = None
    code: str
    language: str
    status: str
    output: Optional[str] = None
    runtime: Optional[float] = None
    test_passed: Optional[int] = None
    test_total: Optional[int] = None
    test_results: Optional[List[bool]] = None  # Individual test results
    created_at: datetime


class ProblemSummary(BaseModel):
    """Answer-free problem description sent to the client."""

    id: str
    title: str
    language: str
    prompt: str
    starter_code: str
