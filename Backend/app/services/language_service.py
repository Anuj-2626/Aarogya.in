from ..languages import (
    DEFAULT_LANGUAGE,
    is_supported_language
)


def select_language(
    explicit_language=None,
    detected_language=None,
    preferred_language=None
) -> str:
    if explicit_language:
        if is_supported_language(explicit_language):
            return explicit_language

        raise ValueError(
            f"Unsupported language code: {explicit_language}"
        )

    if detected_language:
        if is_supported_language(detected_language):
            return detected_language

    if preferred_language:
        if is_supported_language(preferred_language):
            return preferred_language

    return DEFAULT_LANGUAGE


def validate_language_code(language_code: str) -> str:
    if not language_code:
        raise ValueError(
            "Language code cannot be empty"
        )

    if not is_supported_language(language_code):
        raise ValueError(
            f"Unsupported language code: {language_code}"
        )

    return language_code


def get_interview_language(
    interview_language: str | None
) -> str:
    if interview_language:
        return validate_language_code(
            interview_language
        )

    return DEFAULT_LANGUAGE