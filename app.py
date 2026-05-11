import subprocess
import sys

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
from database import Base, SessionLocal, engine
from schemas import SubmissionCreate, SubmissionResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def execute_python_code(code: str) -> dict:
    """Execute Python code with subprocess (Phase 3 will replace this with a Docker sandbox)."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"status": "completed", "output": result.stdout, "error": None}
        return {"status": "error", "output": result.stdout, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "output": "",
            "error": "Code execution timed out (10 second limit)",
        }
    except Exception as e:
        return {"status": "error", "output": "", "error": str(e)}


@app.get("/")
def health_check():
    return {"status": "healthy"}


@app.post("/submit", response_model=SubmissionResponse)
def submit_code(submission: SubmissionCreate, db: Session = Depends(get_db)):
    new_submission = crud.create_submission(db, submission)

    new_submission.status = "running"
    db.commit()

    if submission.language == "python":
        execution_result = execute_python_code(submission.code)
    else:
        execution_result = {
            "status": "error",
            "output": "",
            "error": f"Language '{submission.language}' not supported yet",
        }

    output = execution_result["output"] or execution_result["error"]
    return crud.update_submission(
        db, new_submission, execution_result["status"], output
    )


@app.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def fetch_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = crud.get_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
