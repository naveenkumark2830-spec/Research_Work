from __future__ import annotations

import os
from dotenv import load_dotenv

from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.ai.router import LLMRouter

from .rag import TeddyRAG
from .orchestrator import TeddyOrchestrator


class GeminiAIProvider(GeminiProvider):
    def parse_user_message(self, message: str) -> dict:
        return {
            "intent": "EXPLAIN",
            "text": "HDFS splits files into blocks and distributes them across DataNodes.",
            "command": None,
            "visual_actions": []
        }


def create_teddy_orchestrator(hdfs_service=None) -> TeddyOrchestrator:
    """
    Creates the complete Teddy intelligence stack.

    Primary:
        Gemini

    Fallback:
        Groq

    Knowledge:
        Teddy RAG
    """
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY") or "mock_gemini_key"
    groq_key = os.getenv("GROQ_API_KEY") or "mock_groq_key"

    gemini = GeminiProvider(
        api_key=gemini_key,
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        ),
    )

    groq = GroqProvider(
        api_key=groq_key,
        model=os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        ),
    )

    router = LLMRouter(
        primary=gemini,
        fallback=groq,
    )

    rag = TeddyRAG()

    return TeddyOrchestrator(
        llm_router=router,
        rag=rag,
        hdfs_service=hdfs_service,
    )

