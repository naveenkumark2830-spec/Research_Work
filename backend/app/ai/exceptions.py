from app.core.exceptions import BaseAppException


class AIOrchestratorError(BaseAppException):
    """Base exception for AI Orchestrator errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message=message, status_code=status_code)


class AIProviderError(AIOrchestratorError):
    """Raised when an AI provider fails or is misconfigured."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=503)


class InvalidAIActionError(AIOrchestratorError):
    """Raised when AI proposes an unsafe or invalid action."""

    def __init__(self, message: str):
        super().__init__(message=message, status_code=422)


class LLMError(Exception):
    """Base error for Teddy LLM operations."""


class LLMConfigurationError(LLMError):
    """Raised when a provider is not configured correctly."""


class LLMProviderError(LLMError):
    """Raised when an LLM provider request fails."""


class AllProvidersFailedError(LLMError):
    """Raised when the primary and fallback providers both fail."""
