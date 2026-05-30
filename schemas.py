from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    code: str
    language: str


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    language: str
    status: str
    output: Optional[str] = None
    runtime: Optional[float] = None
    test_passed: Optional[int] = None
    test_total: Optional[int] = None
    test_results: Optional[List[bool]] = None  # Individual test results
    created_at: datetime
