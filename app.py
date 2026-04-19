from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys

from database import SessionLocal, engine, Base
from models import Submission

app = FastAPI()

Base.metadata.create_all(bind=engine)


class CodeSubmission(BaseModel):
    code: str
    language: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_python_code(code: str) -> dict:
    """Execute Python code safely with subprocess (fallback mode)."""
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return {
                "status": "completed",
                "output": result.stdout,
                "error": None
            }
        else:
            return {
                "status": "error",
                "output": result.stdout,
                "error": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "output": "",
            "error": "Code execution timed out (10 second limit)"
        }
    except Exception as e:
        return {
            "status": "error",
            "output": "",
            "error": str(e)
        }


@app.get("/")
def health_check():
    return {"status": "healthy"}


@app.post("/submit")
def submit_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    # Create submission with running status
    new_submission = Submission(
        code=submission.code,
        language=submission.language,
        status="running"
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    # Execute the code
    if submission.language == "python":
        execution_result = execute_python_code(submission.code)
    else:
        execution_result = {
            "status": "error",
            "output": "",
            "error": f"Language '{submission.language}' not supported yet"
        }

    # Update submission with results
    new_submission.status = execution_result["status"]
    new_submission.output = execution_result["output"] or execution_result["error"]
    
    db.commit()
    db.refresh(new_submission)

    return {
        "submission_id": new_submission.id,
        "status": new_submission.status,
        "output": new_submission.output
    }
