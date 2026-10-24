from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..schemas import DoctorDashboardResponse
from ..security import require_role
from ..services.doctor_dashboard_service import get_doctor_dashboard


router = APIRouter(
    prefix="/doctor-dashboard",
    tags=["Doctor Dashboard"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/session/{session_id}",
    response_model=DoctorDashboardResponse,
)
def get_session_dashboard(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("doctor", "admin")),
):
    try:
        return get_doctor_dashboard(db, session_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )