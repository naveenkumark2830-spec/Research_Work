from __future__ import annotations

from collections.abc import Callable

from .exceptions import AllProvidersFailedError, LLMProviderError
from .provider import LLMProvider, LLMRequest, LLMResponse


class LLMRouter:
    """Routes Teddy requests to primary provider and then fallback provider."""

    def __init__(
        self,
        primary: LLMProvider,
        fallback: LLMProvider | None = None,
    ):
        self.primary = primary
        self.fallback = fallback

    async def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            return await self.primary.generate(request)
        except Exception as primary_error:
            if self.fallback is None:
                raise AllProvidersFailedError(
                    f"Primary provider failed: {primary_error}"
                ) from primary_error

            try:
                response = await self.fallback.generate(request)
                return LLMResponse(
                    text=response.text,
                    provider=response.provider,
                    model=response.model,
                    fallback_used=True,
                )
            except Exception as fallback_error:
                raise AllProvidersFailedError(
                    f"Primary provider failed: {primary_error}; "
                    f"fallback provider failed: {fallback_error}"
                ) from fallback_error
