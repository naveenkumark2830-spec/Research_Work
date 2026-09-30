from __future__ import annotations

import asyncio
import os

from groq import Groq

from .exceptions import LLMConfigurationError, LLMProviderError
from .provider import LLMProvider, LLMRequest, LLMResponse


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        if not self.api_key:
            raise LLMConfigurationError("GROQ_API_KEY is not configured")
        self.client = Groq(api_key=self.api_key)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        def call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

        try:
            response = await asyncio.wait_for(asyncio.to_thread(call), timeout=4.0)
            text = response.choices[0].message.content
            if not text:
                raise LLMProviderError("Groq returned an empty response")
            return LLMResponse(text=text, provider=self.name, model=self.model)
        except asyncio.TimeoutError:
            raise LLMProviderError("Groq request timed out after 4 seconds")
        except LLMProviderError:
            raise
        except Exception as exc:
            raise LLMProviderError(f"Groq request failed: {exc}") from exc
