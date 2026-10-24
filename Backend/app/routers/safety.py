from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Interview, SafetyFlag


router = APIRouter(
    prefix="/safety",
    tags=["Safety"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/interview/{interview_id}")
def get_interview_safety_flags(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    flags = db.query(SafetyFlag).filter(
        SafetyFlag.interview_id == interview_id
    ).order_by(
        SafetyFlag.detected_at
    ).all()

    return [
        {
            "safety_flag_id": flag.safety_flag_id,
            "interview_id": flag.interview_id,
            "question_id": flag.question_id,
            "category": flag.category,
            "severity": flag.severity,
            "message": flag.message,
            "detected_at": flag.detected_at,
            "status": flag.status
        }
        for flag in flags
    ]