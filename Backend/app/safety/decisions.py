from dataclasses import dataclass
from enum import Enum


class SafetyDecisionType(str, Enum):
    CLEAR = "clear"
    FLAG = "flag"


@dataclass
class SafetyDecision:
    decision: SafetyDecisionType
    question_code: str
    category: str | None = None
    severity: str | None = None
    message: str | None = None