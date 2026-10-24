import json

from sqlalchemy.orm import Session

from ..models import (
    Answer,
    ClinicalSummary,
    Interview,
    MedicalDocument,
    Patient,
    Question,
    SafetyFlag,
    Session as SessionModel,
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
            patient.date_of_birth.date()
            if patient.date_of_birth
            else None
        ),
        "gender": patient.gender,
        "phone": patient.phone,
        "preferred_language": patient.preferred_language,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
    }


def _serialize_session(session: SessionModel) -> dict:
    return {
        "session_id": session.session_id,
        "patient_id": session.patient_id,
        "language": session.language,
        "status": session.status,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "consent_status": session.consent_status,
        "created_at": session.created_at,
    }


def _serialize_answer(
    answer: Answer,
    question: Question
) -> dict:
    return {
        "answer_id": answer.answer_id,
        "interview_id": answer.interview_id,
        "question_id": answer.question_id,
        "question_code": question.question_code,
        "question_text": question.question_text,
        "history_section": question.history_section,
        "answer_text": answer.answer_text,
        "answer_type": answer.answer_type,
        "answered_at": answer.answered_at,
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

        red_flags = (
            db.query(SafetyFlag)
            .filter(
                SafetyFlag.interview_id == interview.interview_id,
                SafetyFlag.status == "active"
            )
            .order_by(
                SafetyFlag.detected_at.asc(),
                SafetyFlag.safety_flag_id.asc()
            )
            .all()
        )

        interview_data.append({
            "interview": interview,
            "answers": [
                _serialize_answer(answer, question)
                for answer, question in answers
            ],
            "red_flags": red_flags,
        })

    return interview_data


def _serialize_timeline(
    db: Session,
    patient_id: int,
    session_id: int
) -> list[TimelineEvent]:
    return (
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
        extracted_data = _safe_json_loads(
            document.extracted_data
        )

        document_data.append({
            "document_id": document.document_id,
            "session_id": document.session_id,
            "filename": document.filename,
            "file_type": document.file_type,
            "storage_path": document.storage_path,
            "ocr_text": document.ocr_text,
            "ocr_status": document.ocr_status,
            "extracted_data": extracted_data,
            "document_date": document.document_date,
            "created_at": document.created_at,
        })

    return document_data


def _get_latest_summary(
    db: Session,
    session_id: int
) -> ClinicalSummary | None:
    return (
        db.query(ClinicalSummary)
        .filter(
            ClinicalSummary.session_id == session_id
        )
        .order_by(
            ClinicalSummary.generated_at.desc(),
            ClinicalSummary.summary_id.desc()
        )
        .first()
    )


def get_doctor_dashboard(
    db: Session,
    session_id: int
) -> dict:
    """
    Build the complete clinical overview for a doctor
    for one clinical session.

    This service only aggregates existing clinical data.
    It does not generate, modify, or interpret clinical data.
    """

    clinical_session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id
        )
        .first()
    )

    if clinical_session is None:
        raise ValueError("Session not found")

    patient = (
        db.query(Patient)
        .filter(
            Patient.patient_id == clinical_session.patient_id
        )
        .first()
    )

    if patient is None:
        raise ValueError("Patient not found")

    interviews = _serialize_interviews(
        db,
        session_id
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

    latest_summary = _get_latest_summary(
        db,
        session_id
    )

    return {
        "patient": _serialize_patient(patient),
        "session": _serialize_session(clinical_session),
        "interviews": interviews,
        "latest_summary": latest_summary,
        "timeline": timeline,
        "documents": documents,
    }