import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import Answer, Interview, Question
from .timeline_service import create_timeline_event


QUESTION_EVENT_MAPPING = {
    "CC_MAIN": ("symptom", "Chief Complaint"),
    "PMH_DISEASES": ("diagnosis", "Past Medical Condition"),
    "PMH_SURGERY": ("procedure", "Past Surgery / Hospitalization"),
    "MED_DETAILS": ("medication", "Current Medication"),
    "INVESTIGATIONS": ("lab_result", "Previous Investigation"),
    "PREVIOUS_TREATMENT": ("treatment", "Previous Treatment"),
    "AYUSH_DETAILS": ("treatment", "AYUSH Treatment")
}


def create_answer_timeline_event(
    db: Session,
    answer: Answer,
    question: Question,
    interview: Interview
):
    mapping = QUESTION_EVENT_MAPPING.get(
        question.question_code
    )

    if mapping is None:
        return None

    if not answer.answer_text or not answer.answer_text.strip():
        return None

    event_type, title_prefix = mapping

    structured_data = json.dumps(
        {
            "answer_id": answer.answer_id,
            "question_id": question.question_id,
            "question_code": question.question_code,
            "history_section": question.history_section,
            "answer_type": answer.answer_type
        },
        ensure_ascii=False
    )

    return create_timeline_event(
        db=db,
        patient_id=interview.session.patient_id,
        session_id=interview.session_id,
        event_date=answer.answered_at or datetime.now(timezone.utc),
        event_type=event_type,
        title=f"{title_prefix}: {answer.answer_text.strip()}",
        description=(
            "Information reported by the patient "
            "during the clinical interview."
        ),
        source_type="interview",
        source_id=answer.answer_id,
        structured_data=structured_data
    )