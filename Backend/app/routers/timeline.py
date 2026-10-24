from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    TimelineEventCreate,
    TimelineEventResponse,
    TimelineEventListResponse
)
from ..services.timeline_service import (
    create_timeline_event,
    get_timeline_event,
    get_patient_timeline
)

router = APIRouter(
    prefix="/timeline",
    tags=["Timeline"]
)


@router.post(
    "/events",
    response_model=TimelineEventResponse
)
def create_event(
    event: TimelineEventCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_timeline_event(
            db=db,
            patient_id=event.patient_id,
            session_id=event.session_id,
            event_date=event.event_date,
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            source_type=event.source_type,
            source_id=event.source_id,
            structured_data=event.structured_data
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


@router.get(
    "/events/{event_id}",
    response_model=TimelineEventResponse
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = get_timeline_event(
        db=db,
        event_id=event_id
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Timeline event not found"
        )

    return event


@router.get(
    "/patient/{patient_id}",
    response_model=TimelineEventListResponse
)
def get_patient_events(
    patient_id: int,
    db: Session = Depends(get_db)
):
    try:
        events = get_patient_timeline(
            db=db,
            patient_id=patient_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    return TimelineEventListResponse(
        patient_id=patient_id,
        events=events,
        total_events=len(events)
    )