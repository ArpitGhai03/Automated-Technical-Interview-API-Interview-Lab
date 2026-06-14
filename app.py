from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import problems
import sandbox
from database import Base, SessionLocal, engine
from schemas import ProblemSummary, SubmissionCreate, SubmissionResponse

app = FastAPI(title="Automated Technical Interview API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _format_output(result: dict) -> str:
    """Build the human-readable output blob stored on the submission."""
    parts = []
    if result.get("output"):
        parts.append(result["output"].rstrip())
    if result.get("error"):
        parts.append(f"Error: {result['error']}")
    test_results = result.get("test_results") or []
    if test_results:
        lines = ["Test Results:"]
        for i, passed in enumerate(test_results):
            lines.append(f"  Test {i + 1}: {'PASSED' if passed else 'FAILED'}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts).strip() or "(no output)"


@app.get("/")
def health_check():
    return {"status": "healthy", "sandbox": sandbox.sandbox_mode()}


@app.get("/problems", response_model=List[ProblemSummary])
def get_problems():
    return problems.list_problems()


@app.post("/submit", response_model=SubmissionResponse)
def submit_code(submission: SubmissionCreate, db: Session = Depends(get_db)):
    problem = problems.get_problem(submission.problem_id)
    if problem is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown problem '{submission.problem_id}'"
        )

    new_submission = crud.create_submission(db, submission, language=problem.language)
    new_submission.status = "running"
    db.commit()

    result = sandbox.run(problem, submission.code)

    if result.get("sandbox_unavailable"):
        # Record the attempt, then signal that this is an infrastructure issue.
        crud.update_submission(db, new_submission, "error", result.get("error"))
        raise HTTPException(status_code=503, detail=result.get("error"))

    return crud.update_submission(
        db,
        new_submission,
        result.get("status", "error"),
        _format_output(result),
        runtime=result.get("runtime"),
        test_passed=result.get("test_passed"),
        test_total=result.get("test_total"),
        test_results=result.get("test_results"),
    )


@app.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def fetch_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = crud.get_submission(db, submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
