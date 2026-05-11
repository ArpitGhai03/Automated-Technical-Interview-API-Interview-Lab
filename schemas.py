from datetime import datetime
from typing import Optional

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
    created_at: datetime
