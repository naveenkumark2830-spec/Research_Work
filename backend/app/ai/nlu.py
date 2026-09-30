from __future__ import annotations

import json
import re

from .exceptions import LLMProviderError
from .intent import IntentType
from .action import IntentResult
from .prompts import TEDDY_NLU_SYSTEM_PROMPT
from .provider import LLMRequest
from .router import LLMRouter


class TeddyNLU:

    def __init__(self, router: LLMRouter):
        self.router = router

    async def understand(self, user_text: str) -> IntentResult:

        request = LLMRequest(
            prompt=user_text,
            system_prompt=TEDDY_NLU_SYSTEM_PROMPT,
            temperature=0.0,
            max_tokens=500,
        )

        response = await self.router.generate(request)

        data = self._parse_json(response.text)

        return self._validate_result(data)

    @staticmethod
    def _parse_json(text: str) -> dict:

        text = text.strip()

        # Remove markdown code fences if the provider adds them.
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

        try:
            return json.loads(text)

        except json.JSONDecodeError as exc:
            raise LLMProviderError(
                f"Teddy returned invalid JSON: {exc}"
            ) from exc

    @staticmethod
    def _validate_result(
        data: dict,
    ) -> IntentResult:

        raw_intent = data.get(
            "intent",
            "UNKNOWN",
        )

        try:
            intent = IntentType(raw_intent)

        except ValueError:
            intent = IntentType.UNKNOWN

        confidence = float(
            data.get("confidence", 0.0)
        )

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        parameters = data.get(
            "parameters",
            {},
        )

        if not isinstance(parameters, dict):
            parameters = {}

        return IntentResult(
            intent=intent,
            confidence=confidence,
            parameters=parameters,
        )
