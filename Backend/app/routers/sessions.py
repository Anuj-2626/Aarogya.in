from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Patient, Session as SessionModel, Consent
from ..schemas import SessionCreate, SessionResponse, SessionUpdate
from ..services.language_service import select_language


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=201
)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.patient_id == session_data.patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    try:
        selected_language = select_language(
            explicit_language=session_data.language,
            preferred_language=patient.preferred_language
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    new_session = SessionModel(
        patient_id=session_data.patient_id,
        session_type=session_data.session_type,
        language=selected_language
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get(
    "/",
    response_model=list[SessionResponse]
)
def get_sessions(
    db: Session = Depends(get_db)
):
    return db.query(SessionModel).all()


@router.get(
    "/{session_id}",
    response_model=SessionResponse
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session


@router.put(
    "/{session_id}",
    response_model=SessionResponse
)
def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    update_data = session_data.model_dump(
        exclude_unset=True
    )

    # ---------------------------------------------------------
    # Handle normal Session fields
    # ---------------------------------------------------------

    if "session_type" in update_data:
        session.session_type = update_data["session_type"]

    if "language" in update_data:
        session.language = update_data["language"]

    if "status" in update_data:
        session.status = update_data["status"]

        if (
            update_data["status"] == "completed"
            and session.ended_at is None
        ):
            session.ended_at = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # Handle consent_status through Consent records
    # ---------------------------------------------------------

    if "consent_status" in update_data:
        requested_consent_status = update_data["consent_status"]

        consent = (
            db.query(Consent)
            .filter(
                Consent.session_id == session.session_id
            )
            .order_by(Consent.consent_id.desc())
            .first()
        )

        if consent is None:
            consent = Consent(
                session_id=session.session_id,
                consent_type="clinical_workflow",
                status=requested_consent_status,
                granted_at=(
                    datetime.now(timezone.utc)
                    if requested_consent_status == "granted"
                    else None
                ),
                revoked_at=(
                    datetime.now(timezone.utc)
                    if requested_consent_status == "withdrawn"
                    else None
                )
            )

            db.add(consent)

        else:
            consent.status = requested_consent_status

            if requested_consent_status == "granted":
                consent.granted_at = datetime.now(timezone.utc)
                consent.revoked_at = None

            elif requested_consent_status == "withdrawn":
                consent.revoked_at = datetime.now(timezone.utc)

            elif requested_consent_status == "pending":
                consent.granted_at = None
                consent.revoked_at = None

    db.commit()
    db.refresh(session)

    return session