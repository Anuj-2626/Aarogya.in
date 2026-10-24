FOLLOW_UP_RULES = {
    "MED_CURRENT": {
        "yes": "MED_DETAILS",
        "no": None
    },
    "ALLERGY": {
        "yes": "ALLERGY_DETAILS",
        "no": None
    },
    "AYUSH_USE": {
        "yes": "AYUSH_DETAILS",
        "no": None
    }
}


def normalize_answer(answer: str) -> str:
    return answer.strip().lower()


def get_follow_up_question(
    question_code: str,
    answer: str
) -> str | None:
    rules = FOLLOW_UP_RULES.get(question_code)

    if rules is None:
        return None

    normalized_answer = normalize_answer(answer)

    return rules.get(normalized_answer)