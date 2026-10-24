from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Session as SessionModel, Consent
from ..schemas import ConsentCreate, ConsentResponse, ConsentUpdate


router = APIRouter(
    prefix="/consents",
    tags=["Consents"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=ConsentResponse,
    status_code=201
)
def create_consent(
    consent_data: ConsentCreate,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.session_id == consent_data.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    now = datetime.now(timezone.utc)

    if consent_data.status == "granted":
        granted_at = now
        revoked_at = None

    elif consent_data.status == "withdrawn":
        granted_at = None
        revoked_at = now

    else:
        granted_at = None
        revoked_at = None

    new_consent = Consent(
        session_id=consent_data.session_id,
        consent_type=consent_data.consent_type,
        status=consent_data.status,
        granted_at=granted_at,
        revoked_at=revoked_at
    )

    db.add(new_consent)
    db.commit()
    db.refresh(new_consent)

    return new_consent


@router.get(
    "/",
    response_model=list[ConsentResponse]
)
def get_consents(
    db: Session = Depends(get_db)
):
    return db.query(Consent).all()


@router.get(
    "/{consent_id}",
    response_model=ConsentResponse
)
def get_consent(
    consent_id: int,
    db: Session = Depends(get_db)
):
    consent = db.query(Consent).filter(
        Consent.consent_id == consent_id
    ).first()

    if consent is None:
        raise HTTPException(
            status_code=404,
            detail="Consent not found"
        )

    return consent


@router.put(
    "/{consent_id}",
    response_model=ConsentResponse
)
def update_consent(
    consent_id: int,
    consent_data: ConsentUpdate,
    db: Session = Depends(get_db)
):
    consent = db.query(Consent).filter(
        Consent.consent_id == consent_id
    ).first()

    if consent is None:
        raise HTTPException(
            status_code=404,
            detail="Consent not found"
        )

    update_data = consent_data.model_dump(
        exclude_unset=True
    )

    new_status = update_data.get("status")

    if new_status == "granted":
        consent.status = "granted"
        consent.granted_at = datetime.now(timezone.utc)
        consent.revoked_at = None

    elif new_status == "withdrawn":
        consent.status = "withdrawn"
        consent.revoked_at = datetime.now(timezone.utc)

    elif new_status == "pending":
        consent.status = "pending"
        consent.granted_at = None
        consent.revoked_at = None

    db.commit()
    db.refresh(consent)

    return consent