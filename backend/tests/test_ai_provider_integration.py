import asyncio
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
import pytest

from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.ai.provider import LLMRequest
from app.ai.router import LLMRouter

# Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)


@pytest.mark.asyncio
async def test_real_gemini_provider():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY not configured")

    provider = GeminiProvider()
    request = LLMRequest(
        prompt="Explain HDFS block size in exactly one sentence.",
        system_prompt="You are Teddy, an educational Hadoop AI assistant."
    )
    response = await provider.generate(request)

    print("\n[REAL API TEST] Gemini Response:")
    print(f"Provider: {response.provider} ({response.model})")
    print(f"Text: {response.text}\n")

    assert response.text is not None
    assert len(response.text.strip()) > 0
    assert response.provider == "gemini"


@pytest.mark.asyncio
async def test_real_groq_provider():
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        pytest.skip("GROQ_API_KEY not configured")

    provider = GroqProvider()
    request = LLMRequest(
        prompt="Explain HDFS replication factor in exactly one sentence.",
        system_prompt="You are Teddy, an educational Hadoop AI assistant."
    )
    response = await provider.generate(request)

    print("\n[REAL API TEST] Groq Response:")
    print(f"Provider: {response.provider} ({response.model})")
    print(f"Text: {response.text}\n")

    assert response.text is not None
    assert len(response.text.strip()) > 0
    assert response.provider == "groq"


@pytest.mark.asyncio
async def test_real_router_integration():
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    if not gemini_key or not groq_key:
        pytest.skip("Both GEMINI_API_KEY and GROQ_API_KEY are required for router integration test")

    primary = GeminiProvider()
    fallback = GroqProvider()
    router = LLMRouter(primary=primary, fallback=fallback)

    request = LLMRequest(
        prompt="Describe the NameNode role in HDFS in one sentence.",
        system_prompt="You are Teddy, an educational Hadoop AI assistant."
    )
    response = await router.generate(request)

    print("\n[REAL API TEST] Router Response:")
    print(f"Provider Used: {response.provider} (Fallback Used: {response.fallback_used})")
    print(f"Text: {response.text}\n")

    assert response.text is not None
    assert len(response.text.strip()) > 0


async def main():
    print("=========================================")
    print("  RUNNING REAL LLM PROVIDER SMOKE TEST   ")
    print("=========================================")
    try:
        await test_real_gemini_provider()
    except Exception as e:
        print(f"Gemini Test Exception: {e}")

    try:
        await test_real_groq_provider()
    except Exception as e:
        print(f"Groq Test Exception: {e}")

    try:
        await test_real_router_integration()
    except Exception as e:
        print(f"Router Test Exception: {e}")

    print("=========================================")
    print("Smoke Test Execution Finished")


if __name__ == "__main__":
    asyncio.run(main())
