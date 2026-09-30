from __future__ import annotations

import asyncio
import os

from google import genai
from google.genai import types

from .exceptions import LLMConfigurationError, LLMProviderError
from .provider import LLMProvider, LLMRequest, LLMResponse


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        if not self.api_key:
            raise LLMConfigurationError("GEMINI_API_KEY is not configured")
        self.client = genai.Client(api_key=self.api_key)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        contents = request.prompt
        config = types.GenerateContentConfig(
            system_instruction=request.system_prompt,
            temperature=request.temperature,
            max_output_tokens=request.max_tokens,
        )

        def call():
            return self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )

        try:
            response = await asyncio.wait_for(asyncio.to_thread(call), timeout=4.0)
            text = getattr(response, "text", None)
            if not text:
                raise LLMProviderError("Gemini returned an empty response")
            return LLMResponse(text=text, provider=self.name, model=self.model)
        except asyncio.TimeoutError:
            raise LLMProviderError("Gemini request timed out after 4 seconds")
        except LLMProviderError:
            raise
        except Exception as exc:
            raise LLMProviderError(f"Gemini request failed: {exc}") from exc
