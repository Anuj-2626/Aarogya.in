from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Interview, Question
from ..schemas import QuestionResponse
from ..services.language_service import get_interview_language
from ..services.translation_service import translation_service


router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "/interview/{interview_id}",
    response_model=list[QuestionResponse]
)
def get_interview_questions(
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

    try:
        interview_language = get_interview_language(
            interview.language
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    questions = db.query(Question).filter(
        Question.interview_id == interview_id
    ).order_by(
        Question.sequence_number
    ).all()

    response = []

    for question in questions:
        try:
            question_text = (
                translation_service.translate_question(
                    question_text=question.question_text,
                    source_language="en",
                    target_language=interview_language,
                    question_code=question.question_code
                )
            )
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error)
            )
        except NotImplementedError:
            question_text = question.question_text

        response.append(
            QuestionResponse(
                question_id=question.question_id,
                interview_id=question.interview_id,
                question_code=question.question_code,
                question_text=question_text,
                question_type=question.question_type,
                history_section=question.history_section,
                sequence_number=question.sequence_number,
                is_required=question.is_required,
                parent_question_id=question.parent_question_id,
                language=interview_language,
                created_at=question.created_at
            )
        )

    return response
