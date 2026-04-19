from pydantic import BaseModel

class SubmissionCreate(BaseModel):
    code: str
    language: str