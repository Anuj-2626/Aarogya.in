from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Interview, Question, Session as SessionModel
from ..question_bank.clinical_questions import CLINICAL_QUESTIONS
from ..schemas import InterviewCreate, InterviewResponse, InterviewUpdate
from ..security import require_consent
from ..services.language_service import select_language


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=InterviewResponse,
    status_code=201
)
def create_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.session_id == interview_data.session_id
    ).first()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    require_consent(
        session_id=interview_data.session_id,
        consent_type="ai_processing",
        db=db
    )

    try:
        selected_language = select_language(
            explicit_language=interview_data.language,
            preferred_language=session.language
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    existing_interview = db.query(Interview).filter(
        Interview.session_id == interview_data.session_id
    ).first()

    if existing_interview is not None:
        raise HTTPException(
            status_code=409,
            detail="An interview already exists for this session"
        )

    new_interview = Interview(
        session_id=interview_data.session_id,
        interview_type=interview_data.interview_type,
        language=selected_language,
        status="not_started"
    )

    db.add(new_interview)
    db.flush()

    question_map = {}

    for question_data in CLINICAL_QUESTIONS:
        new_question = Question(
            interview_id=new_interview.interview_id,
            question_code=question_data["question_code"],
            question_text=question_data["question_text"],
            question_type=question_data["question_type"],
            history_section=question_data["history_section"],
            sequence_number=question_data["sequence"],
            is_required=question_data["required"],
            parent_question_id=None
        )

        db.add(new_question)
        db.flush()

        question_map[
            question_data["question_code"]
        ] = new_question.question_id

    for question_data in CLINICAL_QUESTIONS:
        parent_code = question_data["parent_question"]

        if parent_code is None:
            continue

        question_id = question_map.get(
            question_data["question_code"]
        )

        parent_question_id = question_map.get(
            parent_code
        )

        if question_id is None:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Question '{question_data['question_code']}' "
                    "was not created correctly"
                )
            )

        if parent_question_id is None:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Parent question '{parent_code}' "
                    f"for '{question_data['question_code']}' "
                    "was not found"
                )
            )

        question = db.query(Question).filter(
            Question.question_id == question_id
        ).first()

        question.parent_question_id = parent_question_id

    first_question = db.query(Question).filter(
        Question.interview_id == new_interview.interview_id
    ).order_by(
        Question.sequence_number
    ).first()

    if first_question is not None:
        new_interview.current_question_id = (
            first_question.question_id
        )

    db.commit()
    db.refresh(new_interview)

    return new_interview


@router.get(
    "/",
    response_model=list[InterviewResponse]
)
def get_interviews(
    db: Session = Depends(get_db)
):
    return db.query(Interview).all()


@router.get(
    "/{interview_id}",
    response_model=InterviewResponse
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    return interview


@router.put(
    "/{interview_id}",
    response_model=InterviewResponse
)
def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.interview_id == interview_id
    ).first()

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found"
        )

    update_data = interview_data.model_dump(
        exclude_unset=True
    )

    new_status = update_data.get("status")

    if new_status == "in_progress":
        if interview.started_at is None:
            interview.started_at = datetime.now(timezone.utc)

    elif new_status == "completed":
        interview.completed_at = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(interview, field, value)

    db.commit()
    db.refresh(interview)

    return interview
