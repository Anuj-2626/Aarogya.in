from .exceptions import AIProviderError, AIValidationError
from .provider import AIProvider


class AIInterviewService:

    def __init__(self, provider: AIProvider):
        self.provider = provider

    def generate_interview_response(
        self,
        question: str,
        answer: str
    ) -> dict:
        """
        Analyze a patient's answer during a clinical interview.
        """

        if not question or not question.strip():
            raise AIValidationError(
                "Interview question cannot be empty"
            )

        if not answer or not answer.strip():
            raise AIValidationError(
                "Patient answer cannot be empty"
            )

        try:
            response = self.provider.analyze_clinical_answer(
                question=question,
                answer=answer
            )
        except Exception as error:
            raise AIProviderError(
                "AI provider failed while analyzing the clinical answer"
            ) from error

        if not isinstance(response, dict):
            raise AIProviderError(
                "AI provider returned an invalid clinical response"
            )

        return response

    def generate_follow_up_question(
        self,
        question: str,
        answer: str
    ) -> str | None:
        """
        Generate an AI-powered follow-up question.
        """

        if not question or not question.strip():
            raise AIValidationError(
                "Interview question cannot be empty"
            )

        if not answer or not answer.strip():
            raise AIValidationError(
                "Patient answer cannot be empty"
            )

        try:
            response = self.provider.generate_follow_up(
                question=question,
                answer=answer
            )
        except Exception as error:
            raise AIProviderError(
                "AI provider failed while generating a follow-up question"
            ) from error

        if response is not None and not isinstance(response, str):
            raise AIProviderError(
                "AI provider returned an invalid follow-up question"
            )

        if isinstance(response, str) and not response.strip():
            return None

        return response

    def generate_general_response(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:
        """
        Generate a general AI response.
        """

        if not prompt or not prompt.strip():
            raise AIValidationError(
                "AI prompt cannot be empty"
            )

        try:
            response = self.provider.generate_response(
                prompt=prompt,
                system_prompt=system_prompt
            )
        except Exception as error:
            raise AIProviderError(
                "AI provider failed while generating a response"
            ) from error

        if not isinstance(response, str):
            raise AIProviderError(
                "AI provider returned an invalid response"
            )

        if not response.strip():
            raise AIProviderError(
                "AI provider returned an empty response"
            )

        return response