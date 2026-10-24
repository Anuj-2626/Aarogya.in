from sqlalchemy.orm import Session

from ..models import Answer, Interview, Question
from .decision import AdaptiveDecision, AdaptiveDecisionType
from .rules import get_follow_up_question


class AdaptiveQuestionEngine:
    """
    Determines the next relevant question in a clinical interview.

    The engine uses deterministic rules for now.
    AI-based interpretation can be integrated later without
    changing the engine's external interface.
    """

    def determine_next_question(
        self,
        interview_id: int,
        question_id: int,
        answer_text: str,
        db: Session
    ) -> AdaptiveDecision:

        interview = db.query(Interview).filter(
            Interview.interview_id == interview_id
        ).first()

        if interview is None:
            raise ValueError("Interview not found")

        current_question = db.query(Question).filter(
            Question.question_id == question_id,
            Question.interview_id == interview_id
        ).first()

        if current_question is None:
            raise ValueError(
                "Question does not belong to this interview"
            )

        follow_up_code = get_follow_up_question(
            current_question.question_code,
            answer_text
        )

        if follow_up_code is not None:
            follow_up_question = db.query(Question).filter(
                Question.interview_id == interview_id,
                Question.question_code == follow_up_code
            ).first()

            if follow_up_question is not None:
                return AdaptiveDecision(
                    decision=AdaptiveDecisionType.ASK,
                    next_question_id=follow_up_question.question_id,
                    reason=(
                        f"Answer to {current_question.question_code} "
                        f"triggered follow-up {follow_up_code}"
                    )
                )

        next_question = self._find_next_relevant_question(
            interview_id=interview_id,
            current_question=current_question,
            db=db
        )

        if next_question is not None:
            return AdaptiveDecision(
                decision=AdaptiveDecisionType.ASK,
                next_question_id=next_question.question_id,
                reason=(
                    "Selected the next relevant question "
                    "after applying adaptive rules"
                )
            )

        return AdaptiveDecision(
            decision=AdaptiveDecisionType.COMPLETE,
            next_question_id=None,
            reason="No remaining relevant questions in the interview"
        )

    def _find_next_relevant_question(
        self,
        interview_id: int,
        current_question: Question,
        db: Session
    ) -> Question | None:

        remaining_questions = db.query(Question).filter(
            Question.interview_id == interview_id,
            Question.sequence_number >
            current_question.sequence_number
        ).order_by(
            Question.sequence_number
        ).all()

        for question in remaining_questions:
            if question.parent_question_id is None:
                return question

            parent_answer = db.query(Answer).join(
                Question,
                Answer.question_id == Question.question_id
            ).filter(
                Answer.interview_id == interview_id,
                Question.question_code == question.parent_question_id
            ).order_by(
                Answer.answered_at.desc()
            ).first()

            if parent_answer is None:
                continue

            follow_up_code = get_follow_up_question(
                question.parent_question_id,
                parent_answer.answer_text
            )

            if follow_up_code == question.question_code:
                return question

        return None


adaptive_question_engine = AdaptiveQuestionEngine()