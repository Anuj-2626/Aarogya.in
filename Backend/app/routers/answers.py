from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..adaptive.engine import adaptive_question_engine
from ..database import SessionLocal
from ..models import Answer, Interview, Question, SafetyFlag
from ..schemas import AnswerCreate, AnswerResponse
from ..services.ai_clinical_agent import (
    ai_clinical_agent,
)
from ..services.clinical_history_timeline_service import (
    create_answer_timeline_event,
)
from ..services.language_service import (
    get_interview_language,
)
from ..safety.detector import red_flag_detector


router = APIRouter(
    prefix="/answers",
    tags=["Answers"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=AnswerResponse,
    status_code=201,
)
def create_answer(
    answer_data: AnswerCreate,
    db: Session = Depends(get_db),
):
    interview = (
        db.query(Interview)
        .filter(
            Interview.interview_id
            == answer_data.interview_id
        )
        .first()
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    question = (
        db.query(Question)
        .filter(
            Question.question_id
            == answer_data.question_id
        )
        .first()
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    if (
        question.interview_id
        != interview.interview_id
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Question does not belong "
                "to this interview"
            ),
        )

    try:
        get_interview_language(
            interview.language
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        )

    # --------------------------------------------------------
    # 1. Deterministic safety detection
    # --------------------------------------------------------

    safety_decision = red_flag_detector.detect(
        question_code=question.question_code,
        answer=answer_data.answer_text,
    )

    # --------------------------------------------------------
    # 2. Persist answer
    # --------------------------------------------------------

    new_answer = Answer(
        interview_id=answer_data.interview_id,
        question_id=answer_data.question_id,
        answer_text=answer_data.answer_text,
        answer_type=answer_data.answer_type,
    )

    db.add(new_answer)
    db.flush()

    # --------------------------------------------------------
    # 3. Persist safety flag
    # --------------------------------------------------------

    if (
        safety_decision.decision.value
        == "flag"
    ):
        existing_flag = (
            db.query(SafetyFlag)
            .filter(
                SafetyFlag.interview_id
                == interview.interview_id,
                SafetyFlag.question_id
                == question.question_id,
                SafetyFlag.status == "active",
            )
            .first()
        )

        if existing_flag is None:
            new_flag = SafetyFlag(
                interview_id=interview.interview_id,
                question_id=question.question_id,
                category=safety_decision.category,
                severity=safety_decision.severity,
                message=safety_decision.message,
                status="active",
            )

            db.add(new_flag)

    # --------------------------------------------------------
    # 4. Ask the real AI agent
    # --------------------------------------------------------

    ai_decision = (
        ai_clinical_agent.choose_next_question(
            interview=interview,
            current_question=question,
            current_answer=answer_data.answer_text,
            db=db,
        )
    )

    next_question = None

    if (
        ai_decision is not None
        and ai_decision.question_code is not None
    ):
        next_question = (
            db.query(Question)
            .filter(
                Question.interview_id
                == interview.interview_id,
                Question.question_code
                == ai_decision.question_code,
            )
            .first()
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Use the AI-generated wording for the next question.
        # The clinical question code remains controlled by
        # the predefined question bank.
        # ----------------------------------------------------

        if (
            next_question is not None
            and ai_decision.question_text
        ):
            next_question.question_text = (
                ai_decision.question_text
            )

    # --------------------------------------------------------
    # 5. Deterministic fallback
    # --------------------------------------------------------

    if next_question is not None:
        interview.current_question_id = (
            next_question.question_id
        )

    else:
        try:
            decision = (
                adaptive_question_engine
                .determine_next_question(
                    interview_id=interview.interview_id,
                    question_id=question.question_id,
                    answer_text=answer_data.answer_text,
                    db=db,
                )
            )

        except ValueError as error:
            db.rollback()

            raise HTTPException(
                status_code=400,
                detail=str(error),
            )

        if decision.next_question_id is not None:
            interview.current_question_id = (
                decision.next_question_id
            )

        else:
            interview.current_question_id = None

    # --------------------------------------------------------
    # 6. Complete interview
    # --------------------------------------------------------

    if interview.current_question_id is None:
        interview.status = "completed"

    # --------------------------------------------------------
    # 7. Timeline
    # --------------------------------------------------------

    create_answer_timeline_event(
        db=db,
        answer=new_answer,
        question=question,
        interview=interview,
    )

    # --------------------------------------------------------
    # 8. Atomic commit
    # --------------------------------------------------------

    db.commit()
    db.refresh(new_answer)

    return new_answer


@router.get(
    "/interview/{interview_id}",
    response_model=list[AnswerResponse],
)
def get_interview_answers(
    interview_id: int,
    db: Session = Depends(get_db),
):
    interview = (
        db.query(Interview)
        .filter(
            Interview.interview_id
            == interview_id
        )
        .first()
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return (
        db.query(Answer)
        .filter(
            Answer.interview_id
            == interview_id
        )
        .order_by(
            Answer.answered_at
        )
        .all()
    )


@router.get(
    "/{answer_id}",
    response_model=AnswerResponse,
)
def get_answer(
    answer_id: int,
    db: Session = Depends(get_db),
):
    answer = (
        db.query(Answer)
        .filter(
            Answer.answer_id
            == answer_id
        )
        .first()
    )

    if answer is None:
        raise HTTPException(
            status_code=404,
            detail="Answer not found",
        )

    return answer