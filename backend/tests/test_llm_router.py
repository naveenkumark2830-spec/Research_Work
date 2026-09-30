import pytest
from app.ai.exceptions import AllProvidersFailedError, LLMProviderError
from app.ai.provider import LLMProvider, LLMRequest, LLMResponse
from app.ai.router import LLMRouter


class DummySuccessProvider(LLMProvider):
    name = "dummy_primary"
    model = "dummy-v1"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="Primary response", provider=self.name, model=self.model)


class DummyFailingProvider(LLMProvider):
    name = "dummy_failing"
    model = "dummy-v1"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise LLMProviderError("Provider execution failed")


class DummyFallbackProvider(LLMProvider):
    name = "dummy_fallback"
    model = "dummy-v2"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="Fallback response", provider=self.name, model=self.model)


@pytest.mark.asyncio
async def test_router_primary_success():
    primary = DummySuccessProvider()
    fallback = DummyFallbackProvider()
    router = LLMRouter(primary=primary, fallback=fallback)

    request = LLMRequest(prompt="Test prompt")
    response = await router.generate(request)

    assert response.text == "Primary response"
    assert response.provider == "dummy_primary"
    assert response.fallback_used is False


@pytest.mark.asyncio
async def test_router_primary_failure_fallback_success():
    primary = DummyFailingProvider()
    fallback = DummyFallbackProvider()
    router = LLMRouter(primary=primary, fallback=fallback)

    request = LLMRequest(prompt="Test prompt")
    response = await router.generate(request)

    assert response.text == "Fallback response"
    assert response.provider == "dummy_fallback"
    assert response.fallback_used is True


@pytest.mark.asyncio
async def test_router_all_providers_failed():
    primary = DummyFailingProvider()
    fallback = DummyFailingProvider()
    router = LLMRouter(primary=primary, fallback=fallback)

    request = LLMRequest(prompt="Test prompt")
    with pytest.raises(AllProvidersFailedError):
        await router.generate(request)
