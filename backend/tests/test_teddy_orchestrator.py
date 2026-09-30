import pytest

from app.jarvis.orchestrator import TeddyOrchestrator
from app.jarvis.schemas import TeddyRequest


class FakeRAG:

    def build_context(self, question, top_k=5):
        return """
        NameNode stores HDFS metadata.
        DataNodes store actual blocks.
        HDFS files are divided into blocks according to block size.
        Replication provides fault tolerance.
        """


class FakeLLM:

    async def generate(self, request):

        class Response:
            text = """
            {
              "intent": "explain NameNode",
              "answer": "The NameNode manages HDFS metadata.",
              "voice_text": "The NameNode manages the metadata of HDFS.",
              "simulation_required": false,
              "simulation_action": {
                "action": "none",
                "parameters": {}
              },
              "visualization": [
                {
                  "type": "show_namenode",
                  "title": "NameNode",
                  "description": "Highlight the NameNode and its metadata role.",
                  "data": {},
                  "duration_ms": 1500
                }
              ],
              "sources": [
                "Hadoop knowledge context"
              ]
            }
            """

        return Response()


@pytest.mark.asyncio
async def test_teddy_orchestrator():

    orchestrator = TeddyOrchestrator(
        llm_router=FakeLLM(),
        rag=FakeRAG(),
        hdfs_service=None,
    )

    request = TeddyRequest(
        session_id="test-session",
        user_id="test-user",
        message="What does the NameNode do?",
    )

    response = await orchestrator.process(request)

    assert response.plan.intent == "explain NameNode"

    assert (
        response.plan.simulation_required
        is False
    )

    assert (
        response.plan.visualization[0].type
        == "show_namenode"
    )

    assert (
        "NameNode"
        in response.plan.answer
    )
