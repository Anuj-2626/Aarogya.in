from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai.provider import AIProvider
from ..ai.summary_service import generate_clinical_summary
from ..database import SessionLocal
from ..models import ClinicalSummary
from ..schemas import (
    ClinicalSummaryResponse,
)
from ..services.summary_input_service import build_summary_input


router = APIRouter(
    prefix="/summaries",
    tags=["Clinical Summaries"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_ai_provider() -> AIProvider:
    """
    Return the configured AI provider.

    A concrete provider will be connected when the external
    AI integration is implemented.
    """
    raise HTTPException(
        status_code=503,
        detail="AI provider is not configured"
    )


@router.post(
    "/session/{session_id}",
    response_model=ClinicalSummaryResponse,
    status_code=201
)
def create_session_summary(
    session_id: int,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider)
):
    try:
        summary_input = build_summary_input(
            db=db,
            session_id=session_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    try:
        summary_text = generate_clinical_summary(
            provider=provider,
            summary_input=summary_input
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    summary = ClinicalSummary(
        session_id=session_id,
        summary_text=summary_text,
        structured_data=None,
        source_version="timeline-v1",
        status="generated"
    )

    db.add(summary)
    db.commit()
    db.refresh(summary)

    return summary


@router.get(
    "/session/{session_id}",
    response_model=list[ClinicalSummaryResponse]
)
def get_session_summaries(
    session_id: int,
    db: Session = Depends(get_db)
):
    summaries = (
        db.query(ClinicalSummary)
        .filter(
            ClinicalSummary.session_id == session_id
        )
        .order_by(
            ClinicalSummary.generated_at.asc(),
            ClinicalSummary.summary_id.asc()
        )
        .all()
    )

    return summaries


@router.get(
    "/{summary_id}",
    response_model=ClinicalSummaryResponse
)
def get_summary(
    summary_id: int,
    db: Session = Depends(get_db)
):
    summary = (
        db.query(ClinicalSummary)
        .filter(
            ClinicalSummary.summary_id == summary_id
        )
        .first()
    )

    if summary is None:
        raise HTTPException(
            status_code=404,
            detail="Clinical summary not found"
        )

    return summary