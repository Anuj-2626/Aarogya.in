from .decisions import SafetyDecision, SafetyDecisionType
from .red_flags import RED_FLAG_RULES, check_red_flag


class RedFlagDetector:

    def detect(
        self,
        question_code: str,
        answer: str
    ) -> SafetyDecision:

        rule = RED_FLAG_RULES.get(question_code)

        if rule is None:
            return SafetyDecision(
                decision=SafetyDecisionType.CLEAR,
                question_code=question_code
            )

        is_flagged = check_red_flag(
            question_code=question_code,
            answer=answer
        )

        if not is_flagged:
            return SafetyDecision(
                decision=SafetyDecisionType.CLEAR,
                question_code=question_code
            )

        return SafetyDecision(
            decision=SafetyDecisionType.FLAG,
            question_code=question_code,
            category=rule["category"],
            severity=rule["severity"],
            message=rule["message"]
        )


red_flag_detector = RedFlagDetector()