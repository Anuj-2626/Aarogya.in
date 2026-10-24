from dataclasses import dataclass
from enum import Enum


class AdaptiveDecisionType(str, Enum):
    ASK = "ask"
    SKIP = "skip"
    COMPLETE = "complete"


@dataclass
class AdaptiveDecision:
    decision: AdaptiveDecisionType
    next_question_id: int | None = None
    reason: str | None = None