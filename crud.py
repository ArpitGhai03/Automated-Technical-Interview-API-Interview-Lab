from typing import Optional

from sqlalchemy.orm import Session

from models import Submission
from schemas import SubmissionCreate


def create_submission(db: Session, submission: SubmissionCreate) -> Submission:
    new_submission = Submission(
        code=submission.code,
        language=submission.language,
        status="pending",
    )
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    return new_submission


def update_submission(
    db: Session,
    submission: Submission,
    status: str,
    output: Optional[str],
    runtime: Optional[float] = None,
    test_passed: Optional[int] = None,
    test_total: Optional[int] = None,
    test_results: Optional[list] = None,
) -> Submission:
    submission.status = status
    submission.output = output
    submission.runtime = runtime
    submission.test_passed = test_passed
    submission.test_total = test_total
    submission.test_results = test_results
    db.commit()
    db.refresh(submission)
    return submission


def get_submission(db: Session, submission_id: int) -> Optional[Submission]:
    return db.query(Submission).filter(Submission.id == submission_id).first()
