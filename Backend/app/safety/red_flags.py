RED_FLAG_RULES = {
    "RED_FLAG_CHEST": {
        "category": "chest_pain",
        "severity": "high",
        "trigger_answers": [
            "yes",
            "y",
            "true"
        ],
        "message": (
            "Potential chest-related red flag detected. "
            "Clinician attention is required."
        )
    },
    "RED_FLAG_BREATHING": {
        "category": "breathing_difficulty",
        "severity": "high",
        "trigger_answers": [
            "yes",
            "y",
            "true"
        ],
        "message": (
            "Potential breathing-related red flag detected. "
            "Clinician attention is required."
        )
    },
    "RED_FLAG_CONSCIOUSNESS": {
        "category": "altered_consciousness",
        "severity": "high",
        "trigger_answers": [
            "yes",
            "y",
            "true"
        ],
        "message": (
            "Potential consciousness-related red flag detected. "
            "Clinician attention is required."
        )
    }
}


def normalize_answer(answer: str) -> str:
    return answer.strip().lower()


def is_red_flag_question(question_code: str) -> bool:
    return question_code in RED_FLAG_RULES


def check_red_flag(
    question_code: str,
    answer: str
) -> bool:
    rule = RED_FLAG_RULES.get(question_code)

    if rule is None:
        return False

    normalized_answer = normalize_answer(answer)

    return normalized_answer in rule["trigger_answers"]