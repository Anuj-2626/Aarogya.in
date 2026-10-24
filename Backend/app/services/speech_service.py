from ..languages import validate_language


class SpeechService:
    """
    Provider-independent foundation for speech processing.

    A real ASR/TTS provider can be integrated later without
    changing the application code that uses this service.
    """

    def speech_to_text(
        self,
        audio_data: bytes,
        language_code: str
    ) -> str:
        validate_language(language_code)

        if not audio_data:
            raise ValueError(
                "Audio data cannot be empty"
            )

        raise NotImplementedError(
            "Speech-to-text provider is not configured yet"
        )

    def text_to_speech(
        self,
        text: str,
        language_code: str
    ) -> bytes:
        validate_language(language_code)

        if not text or not text.strip():
            raise ValueError(
                "Text for speech synthesis cannot be empty"
            )

        raise NotImplementedError(
            "Text-to-speech provider is not configured yet"
        )

    def detect_language(
        self,
        text: str
    ) -> str:
        if not text or not text.strip():
            raise ValueError(
                "Text for language detection cannot be empty"
            )

        raise NotImplementedError(
            "Language detection provider is not configured yet"
        )


speech_service = SpeechService()