from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas import FHIRBundle
from ..security import require_role
from ..services.fhir_service import build_session_fhir_bundle


router = APIRouter(
    prefix="/fhir",
    tags=["FHIR / ABDM"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/session/{session_id}",
    response_model=FHIRBundle,
)
def get_session_fhir_bundle(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role("doctor", "admin")
    ),
):
    try:
        return build_session_fhir_bundle(
            db,
            session_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )