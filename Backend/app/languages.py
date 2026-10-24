
SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native_name": "English",
    },
    "hi": {
        "name": "Hindi",
        "native_name": "हिन्दी",
    },
    "mr": {
        "name": "Marathi",
        "native_name": "मराठी",
    },
}


DEFAULT_LANGUAGE = "en"


def get_supported_languages() -> dict:
    return SUPPORTED_LANGUAGES.copy()


def get_default_language() -> str:
    return DEFAULT_LANGUAGE


def is_supported_language(language_code: str) -> bool:
    return language_code in SUPPORTED_LANGUAGES


def validate_language(language_code: str) -> str:
    if not language_code:
        raise ValueError(
            "Language code cannot be empty"
        )

    if not is_supported_language(language_code):
        raise ValueError(
            f"Unsupported language code: {language_code}"
        )

    return language_code


def get_language(language_code: str) -> dict | None:
    return SUPPORTED_LANGUAGES.get(language_code)
