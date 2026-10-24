import json

from sqlalchemy.orm import Session

from ..models import Patient, Session as ClinicalSession, TimelineEvent


VALID_EVENT_TYPES = {
    "diagnosis",
    "symptom",
    "medication",
    "lab_result",
    "procedure",
    "treatment",
    "document",
    "consultation"
}

VALID_SOURCE_TYPES = {
    "interview",
    "document",
    "system"
}


def create_timeline_event(
    db: Session,
    patient_id: int,
    session_id: int | None,
    event_date,
    event_type: str,
    title: str,
    description: str | None,
    source_type: str,
    source_id: int | None,
    structured_data: str | None
) -> TimelineEvent:

    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    if not patient:
        raise ValueError("Patient not found")

    if session_id is not None:
        clinical_session = db.query(ClinicalSession).filter(
            ClinicalSession.session_id == session_id
        ).first()

        if not clinical_session:
            raise ValueError("Session not found")

        if clinical_session.patient_id != patient_id:
            raise ValueError(
                "Session does not belong to the specified patient"
            )

    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"Invalid event type: {event_type}"
        )

    if source_type not in VALID_SOURCE_TYPES:
        raise ValueError(
            f"Invalid source type: {source_type}"
        )

    if structured_data is not None:
        try:
            json.loads(structured_data)
        except json.JSONDecodeError:
            raise ValueError(
                "structured_data must contain valid JSON"
            )

    timeline_event = TimelineEvent(
        patient_id=patient_id,
        session_id=session_id,
        event_date=event_date,
        event_type=event_type,
        title=title,
        description=description,
        source_type=source_type,
        source_id=source_id,
        structured_data=structured_data
    )

    db.add(timeline_event)
    db.commit()
    db.refresh(timeline_event)

    return timeline_event


def get_timeline_event(
    db: Session,
    event_id: int
) -> TimelineEvent | None:

    return db.query(TimelineEvent).filter(
        TimelineEvent.event_id == event_id
    ).first()


def get_patient_timeline(
    db: Session,
    patient_id: int
) -> list[TimelineEvent]:

    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id
    ).first()

    if not patient:
        raise ValueError("Patient not found")

    events = db.query(TimelineEvent).filter(
        TimelineEvent.patient_id == patient_id
    ).order_by(
        TimelineEvent.event_date.asc().nullslast(),
        TimelineEvent.created_at.asc(),
        TimelineEvent.event_id.asc()
    ).all()

    return events