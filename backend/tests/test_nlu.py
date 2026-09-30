import pytest

from app.ai.action import IntentResult
from app.ai.intent import IntentType
from app.ai.nlu import TeddyNLU
from app.ai.provider import LLMProvider, LLMRequest, LLMResponse
from app.ai.router import LLMRouter
from app.ai.validator import AIActionValidator


class FakeNLUProvider(LLMProvider):

    name = "fake"
    model = "fake-model"

    def __init__(self, response):
        self.response = response

    async def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:

        return LLMResponse(
            text=self.response,
            provider=self.name,
            model=self.model,
        )


@pytest.mark.asyncio
async def test_create_hdfs_intent():

    provider = FakeNLUProvider(
        """
        {
          "intent": "CREATE_HDFS_FILE",
          "confidence": 0.99,
          "parameters": {
            "file_size_mb": 1024,
            "block_size_mb": 128,
            "replication_factor": 3
          }
        }
        """
    )

    router = LLMRouter(primary=provider)

    nlu = TeddyNLU(router)

    result = await nlu.understand(
        "Create a 1 GB HDFS file using 128 MB blocks and replication factor 3."
    )

    assert result.intent == IntentType.CREATE_HDFS_FILE

    assert result.parameters["file_size_mb"] == 1024

    assert result.parameters["block_size_mb"] == 128

    assert result.parameters["replication_factor"] == 3


@pytest.mark.asyncio
async def test_explain_namenode():

    provider = FakeNLUProvider(
        """
        {
          "intent": "EXPLAIN_COMPONENT",
          "confidence": 0.98,
          "parameters": {
            "component": "NameNode"
          }
        }
        """
    )

    router = LLMRouter(primary=provider)

    nlu = TeddyNLU(router)

    result = await nlu.understand(
        "How does the NameNode work?"
    )

    assert result.intent == IntentType.EXPLAIN_COMPONENT

    assert result.parameters["component"] == "NameNode"


def test_validator():

    result = IntentResult(
        intent=IntentType.CREATE_HDFS_FILE,
        confidence=0.99,
        parameters={
            "file_size_mb": 1024,
            "block_size_mb": 128,
            "replication_factor": 3,
        },
    )

    validated = AIActionValidator().validate(result)

    assert validated.intent == IntentType.CREATE_HDFS_FILE
