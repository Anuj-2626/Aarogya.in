class AIServiceError(Exception):
    """Base exception for AI service errors."""
    pass


class AIProviderError(AIServiceError):
    """Raised when an AI provider fails."""
    pass


class AIValidationError(AIServiceError):
    """Raised when AI input or output is invalid."""
    pass