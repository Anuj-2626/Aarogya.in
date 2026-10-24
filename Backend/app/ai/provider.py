from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:
        """
        Generate a response from the AI provider.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_clinical_answer(
        self,
        question: str,
        answer: str
    ) -> dict:
        """
        Analyze a patient's answer in a structured way.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_follow_up(
        self,
        question: str,
        answer: str
    ) -> str | None:
        """
        Generate an appropriate follow-up question.
        """
        raise NotImplementedError