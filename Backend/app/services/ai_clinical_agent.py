import json
import os
from dataclasses import dataclass

from openai import OpenAI
from sqlalchemy.orm import Session

from ..models import Answer, Interview, Question


@dataclass
class AIQuestionDecision:
    question_code: str | None
    question_text: str | None
    reason: str


class AIClinicalAgent:
    DEFAULT_MODEL = "gpt-5.6-luna"

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "mr": "Marathi",
    }

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv(
            "OPENAI_MODEL",
            self.DEFAULT_MODEL,
        )

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def choose_next_question(
        self,
        *,
        interview: Interview,
        current_question: Question,
        current_answer: str,
        db: Session,
    ) -> AIQuestionDecision | None:

        if not self.enabled:
            return None

        language_name = self.SUPPORTED_LANGUAGES.get(
            interview.language
        )

        if language_name is None:
            return None

        questions = (
            db.query(Question)
            .filter(
                Question.interview_id
                == interview.interview_id
            )
            .order_by(Question.sequence_number)
            .all()
        )

        answers = (
            db.query(Answer)
            .filter(
                Answer.interview_id
                == interview.interview_id
            )
            .order_by(Answer.answered_at)
            .all()
        )

        answered_question_ids = {
            answer.question_id
            for answer in answers
        }

        candidate_questions = [
            question
            for question in questions
            if (
                question.question_id
                not in answered_question_ids
                and question.question_id
                != current_question.question_id
            )
        ]

        if not candidate_questions:
            return AIQuestionDecision(
                question_code=None,
                question_text=None,
                reason="No unanswered clinical questions remain.",
            )

        question_by_id = {
            question.question_id: question
            for question in questions
        }

        answer_history = []

        for answer in answers:
            question = question_by_id.get(
                answer.question_id
            )

            if question is None:
                continue

            answer_history.append(
                {
                    "question_code": question.question_code,
                    "question": question.question_text,
                    "answer": answer.answer_text,
                    "section": question.history_section,
                }
            )

        candidate_data = [
            {
                "question_code": question.question_code,
                "question": question.question_text,
                "section": question.history_section,
                "question_type": question.question_type,
                "required": question.is_required,
                "sequence": question.sequence_number,
            }
            for question in candidate_questions
        ]

        instructions = f"""
You are the clinical history-taking assistant for Aarogya.in.

Your ONLY role is to collect useful medical history before
a doctor consultation.

You are NOT a doctor.

You MUST NOT:
- diagnose the patient
- prescribe medicines
- recommend treatment
- claim that a disease is confirmed
- override deterministic safety detection
- invent patient facts
- provide emergency treatment instructions

You ARE allowed to:
- understand the patient's previous answers
- identify the most useful missing clinical information
- choose one appropriate topic from the supplied candidate questions
- rewrite that candidate question naturally
- ask a concise contextual follow-up question
- make the conversation feel natural rather than like a fixed questionnaire

IMPORTANT:

The selected question_code MUST come from the supplied
candidate list.

The question_text does NOT have to be identical to the
candidate question.

You should rewrite the selected question so that it naturally
follows the patient's most recent answer.

For example:

Previous answer:
"I have had stomach pain for three days."

Poor:
"Do you have any associated symptoms?"

Better:
"Since the stomach pain started three days ago, have you also
noticed vomiting, loose motions, fever, or anything else unusual?"

Another example:

Previous answer:
"The pain becomes worse after eating."

Better:
"Does the pain start immediately after eating, or does it take
some time to appear?"

Ask ONE question at a time.

Keep it concise and understandable to an ordinary patient.

Use the patient's selected language:

{language_name}

If the language is Hindi, write the question in natural Hindi.

If the language is Marathi, write the question in natural Marathi.

If the language is English, write natural English.

Do not mix languages unless medically unavoidable.

The candidate question is the clinical coverage constraint.
Your wording should remain medically faithful to that candidate.

Return ONLY JSON.

Expected format:

{{
    "question_code": "EXACT_CANDIDATE_CODE",
    "question_text": "Natural contextual question in the patient's language",
    "reason": "Short explanation in English"
}}

If no suitable question remains:

{{
    "question_code": null,
    "question_text": null,
    "reason": "No suitable unanswered question remains."
}}
"""

        payload = {
            "patient_language": language_name,
            "current_question": {
                "question_code": current_question.question_code,
                "question": current_question.question_text,
                "section": current_question.history_section,
            },
            "current_answer": current_answer,
            "previous_answers": answer_history,
            "candidate_questions": candidate_data,
        }

        try:
            client = OpenAI(
                api_key=self.api_key
            )

            response = client.responses.create(
                model=self.model,
                instructions=instructions,
                input=json.dumps(
                    payload,
                    ensure_ascii=False,
                ),
            )

            output = response.output_text.strip()

            if not output:
                return None

            parsed = json.loads(output)

            question_code = parsed.get(
                "question_code"
            )

            question_text = parsed.get(
                "question_text"
            )

            reason = parsed.get(
                "reason",
                "AI generated the next contextual clinical question.",
            )

            if question_code is None:
                return AIQuestionDecision(
                    question_code=None,
                    question_text=None,
                    reason=str(reason),
                )

            valid_codes = {
                question.question_code
                for question in candidate_questions
            }

            if question_code not in valid_codes:
                return None

            if not isinstance(question_text, str):
                return None

            question_text = question_text.strip()

            if not question_text:
                return None

            return AIQuestionDecision(
                question_code=question_code,
                question_text=question_text,
                reason=str(reason),
            )

        except Exception:
            return None


ai_clinical_agent = AIClinicalAgent()