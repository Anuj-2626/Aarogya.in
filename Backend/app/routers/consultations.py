from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import (
    Consultation,
    Session as SessionModel,
    TimelineEvent,
    User,
)
from ..schemas import (
    ConsultationCreate,
    ConsultationListResponse,
    ConsultationResponse,
    ConsultationUpdate,
)
from ..security import require_role


router = APIRouter(
    prefix="/consultations",
    tags=["Consultations"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=ConsultationResponse,
    status_code=201,
)
def create_consultation(
    consultation_data: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "admin")
    ),
):
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id
            == consultation_data.session_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    existing = (
        db.query(Consultation)
        .filter(
            Consultation.session_id
            == consultation_data.session_id,
            Consultation.doctor_user_id
            == current_user.user_id,
            Consultation.status == "draft",
        )
        .order_by(
            Consultation.consultation_id.desc()
        )
        .first()
    )

    if existing is not None:
        existing.clinical_notes = (
            consultation_data.clinical_notes
        )
        existing.assessment = (
            consultation_data.assessment
        )
        existing.diagnosis = (
            consultation_data.diagnosis
        )
        existing.treatment_plan = (
            consultation_data.treatment_plan
        )
        existing.follow_up = (
            consultation_data.follow_up
        )

        db.commit()
        db.refresh(existing)

        return existing

    consultation = Consultation(
        session_id=consultation_data.session_id,
        doctor_user_id=current_user.user_id,
        status="draft",
        clinical_notes=consultation_data.clinical_notes,
        assessment=consultation_data.assessment,
        diagnosis=consultation_data.diagnosis,
        treatment_plan=consultation_data.treatment_plan,
        follow_up=consultation_data.follow_up,
    )

    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    return consultation


@router.get(
    "/session/{session_id}",
    response_model=ConsultationListResponse,
)
def get_session_consultations(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "admin")
    ),
):
    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    consultations = (
        db.query(Consultation)
        .filter(
            Consultation.session_id == session_id
        )
        .order_by(
            Consultation.created_at.desc()
        )
        .all()
    )

    return ConsultationListResponse(
        session_id=session_id,
        consultations=consultations,
        total_consultations=len(consultations),
    )


@router.get(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "admin")
    ),
):
    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.consultation_id
            == consultation_id
        )
        .first()
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found",
        )

    return consultation


@router.put(
    "/{consultation_id}",
    response_model=ConsultationResponse,
)
def update_consultation(
    consultation_id: int,
    consultation_data: ConsultationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("doctor", "admin")
    ),
):
    consultation = (
        db.query(Consultation)
        .filter(
            Consultation.consultation_id
            == consultation_id
        )
        .first()
    )

    if consultation is None:
        raise HTTPException(
            status_code=404,
            detail="Consultation not found",
        )

    if (
        current_user.role != "admin"
        and consultation.doctor_user_id
        != current_user.user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot modify this consultation",
        )

    update_data = consultation_data.model_dump(
        exclude_unset=True
    )

    for field in (
        "clinical_notes",
        "assessment",
        "diagnosis",
        "treatment_plan",
        "follow_up",
    ):
        if field in update_data:
            setattr(
                consultation,
                field,
                update_data[field],
            )

    requested_status = update_data.get("status")

    if (
        requested_status == "completed"
        and consultation.status != "completed"
    ):
        consultation.status = "completed"
        consultation.completed_at = (
            datetime.now(timezone.utc)
        )

        session = (
            db.query(SessionModel)
            .filter(
                SessionModel.session_id
                == consultation.session_id
            )
            .first()
        )

        if session is not None:
            timeline_event = TimelineEvent(
                patient_id=session.patient_id,
                session_id=session.session_id,
                event_date=datetime.now(timezone.utc),
                event_type="consultation",
                title="Doctor consultation completed",
                description=(
                    consultation.diagnosis
                    or consultation.assessment
                    or "Clinical consultation completed."
                ),
                source_type="consultation",
                source_id=consultation.consultation_id,
            )

            db.add(timeline_event)

    elif (
        requested_status == "draft"
        and consultation.status != "completed"
    ):
        consultation.status = "draft"

    db.commit()
    db.refresh(consultation)

    return consultation