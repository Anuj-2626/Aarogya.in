import json

from sqlalchemy.orm import Session

from ..models import (
    Answer,
    Interview,
    MedicalDocument,
    Patient,
    Question,
    SafetyFlag,
    Session as ClinicalSession,
    TimelineEvent,
)


def _safe_json_loads(value: str | None):
    if not value:
        return None

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def _serialize_patient(patient: Patient) -> dict:
    return {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "date_of_birth": (
            patient.date_of_birth.isoformat()
            if patient.date_of_birth
            else None
        ),
        "gender": patient.gender,
        "preferred_language": patient.preferred_language,
    }


def _serialize_interviews(
    db: Session,
    session_id: int
) -> list[dict]:

    interviews = (
        db.query(Interview)
        .filter(Interview.session_id == session_id)
        .order_by(
            Interview.created_at.asc(),
            Interview.interview_id.asc()
        )
        .all()
    )

    interview_data = []

    for interview in interviews:
        answers = (
            db.query(Answer, Question)
            .join(
                Question,
                Answer.question_id == Question.question_id
            )
            .filter(
                Answer.interview_id == interview.interview_id
            )
            .order_by(
                Question.sequence_number.asc(),
                Answer.answered_at.asc(),
                Answer.answer_id.asc()
            )
            .all()
        )

        answer_data = []

        for answer, question in answers:
            answer_data.append(
                {
                    "answer_id": answer.answer_id,
                    "question_id": question.question_id,
                    "question_code": question.question_code,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "history_section": question.history_section,
                    "sequence_number": question.sequence_number,
                    "answer_text": answer.answer_text,
                    "answer_type": answer.answer_type,
                    "answered_at": (
                        answer.answered_at.isoformat()
                        if answer.answered_at
                        else None
                    ),
                    "source": "patient_interview",
                }
            )

        interview_data.append(
            {
                "interview_id": interview.interview_id,
                "interview_type": interview.interview_type,
                "status": interview.status,
                "language": interview.language,
                "started_at": (
                    interview.started_at.isoformat()
                    if interview.started_at
                    else None
                ),
                "completed_at": (
                    interview.completed_at.isoformat()
                    if interview.completed_at
                    else None
                ),
                "answers": answer_data,
            }
        )

    return interview_data


def _serialize_safety_flags(
    db: Session,
    interview_ids: list[int]
) -> list[dict]:

    if not interview_ids:
        return []

    flags = (
        db.query(SafetyFlag)
        .filter(
            SafetyFlag.interview_id.in_(interview_ids),
            SafetyFlag.status == "active"
        )
        .order_by(
            SafetyFlag.interview_id.asc(),
            SafetyFlag.safety_flag_id.asc()
        )
        .all()
    )

    safety_data = []

    for flag in flags:
        safety_data.append(
            {
                "safety_flag_id": flag.safety_flag_id,
                "interview_id": flag.interview_id,
                "question_id": flag.question_id,
                "category": flag.category,
                "severity": flag.severity,
                "message": flag.message,
                "status": flag.status,
                "source": "red_flag_detector",
            }
        )

    return safety_data


def _serialize_timeline(
    db: Session,
    patient_id: int,
    session_id: int
) -> list[dict]:

    events = (
        db.query(TimelineEvent)
        .filter(
            TimelineEvent.patient_id == patient_id,
            TimelineEvent.session_id == session_id
        )
        .order_by(
            TimelineEvent.event_date.asc().nullslast(),
            TimelineEvent.created_at.asc(),
            TimelineEvent.event_id.asc()
        )
        .all()
    )

    timeline_data = []

    for event in events:
        timeline_data.append(
            {
                "event_id": event.event_id,
                "event_date": (
                    event.event_date.isoformat()
                    if event.event_date
                    else None
                ),
                "event_type": event.event_type,
                "title": event.title,
                "description": event.description,
                "source_type": event.source_type,
                "source_id": event.source_id,
                "structured_data": _safe_json_loads(
                    event.structured_data
                ),
            }
        )

    return timeline_data


def _serialize_documents(
    db: Session,
    session_id: int
) -> list[dict]:

    documents = (
        db.query(MedicalDocument)
        .filter(
            MedicalDocument.session_id == session_id
        )
        .order_by(
            MedicalDocument.document_date.asc().nullslast(),
            MedicalDocument.created_at.asc(),
            MedicalDocument.document_id.asc()
        )
        .all()
    )

    document_data = []

    for document in documents:
        document_data.append(
            {
                "document_id": document.document_id,
                "filename": document.filename,
                "file_type": document.file_type,
                "ocr_status": document.ocr_status,
                "ocr_text": document.ocr_text,
                "extracted_data": _safe_json_loads(
                    document.extracted_data
                ),
                "document_date": (
                    document.document_date.isoformat()
                    if document.document_date
                    else None
                ),
                "source": "medical_document",
            }
        )

    return document_data


def build_summary_input(
    db: Session,
    session_id: int
) -> dict:

    clinical_session = (
        db.query(ClinicalSession)
        .filter(
            ClinicalSession.session_id == session_id
        )
        .first()
    )

    if not clinical_session:
        raise ValueError("Session not found")

    patient = (
        db.query(Patient)
        .filter(
            Patient.patient_id == clinical_session.patient_id
        )
        .first()
    )

    if not patient:
        raise ValueError("Patient not found")

    interviews = _serialize_interviews(
        db,
        session_id
    )

    interview_ids = [
        interview["interview_id"]
        for interview in interviews
    ]

    safety_flags = _serialize_safety_flags(
        db,
        interview_ids
    )

    timeline = _serialize_timeline(
        db,
        patient.patient_id,
        session_id
    )

    documents = _serialize_documents(
        db,
        session_id
    )

    return {
        "session": {
            "session_id": clinical_session.session_id,
            "patient_id": clinical_session.patient_id,
            "session_type": clinical_session.session_type,
            "language": clinical_session.language,
            "status": clinical_session.status,
            "consent_status": clinical_session.consent_status,
            "started_at": (
                clinical_session.started_at.isoformat()
                if clinical_session.started_at
                else None
            ),
            "completed_at": (
                clinical_session.completed_at.isoformat()
                if clinical_session.completed_at
                else None
            ),
        },
        "patient": _serialize_patient(patient),
        "clinical_interviews": interviews,
        "safety_flags": safety_flags,
        "timeline": timeline,
        "medical_documents": documents,
    }