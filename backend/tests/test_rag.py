from pathlib import Path

from app.jarvis.rag import TeddyRAG


def test_rag_index_exists():
    vector_dir = Path("data/chroma")

    assert vector_dir.exists()


def test_hdfs_retrieval():
    rag = TeddyRAG()

    results = rag.retrieve(
        "Why does HDFS replicate blocks across DataNodes?",
        top_k=3,
    )

    assert len(results) > 0

    for result in results:
        assert result["text"]
        assert result["source"]
        assert result["page"]


def test_namenode_retrieval():
    rag = TeddyRAG()

    results = rag.retrieve(
        "What does the NameNode do in HDFS?",
        top_k=3,
    )

    assert len(results) > 0

    context = rag.build_context(
        "What does the NameNode do in HDFS?",
        top_k=3,
    )

    assert "NameNode" in context


if __name__ == "__main__":
    test_rag_index_exists()
    test_hdfs_retrieval()
    test_namenode_retrieval()

    print("RAG TESTS PASSED")
