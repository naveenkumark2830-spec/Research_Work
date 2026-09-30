from app.jarvis.rag import TeddyRAG


def main():
    print("=" * 60)
    print("TEDDY RAG INDEX BUILDER")
    print("=" * 60)

    rag = TeddyRAG()

    print("\nLoading Hadoop knowledge...")
    result = rag.build_index()

    print("\nRAG INDEX CREATED")
    print(f"Documents/chunks : {result['documents']}")
    print(f"Collection       : {result['collection']}")
    print(f"Embedding model  : {result['embedding_model']}")
    print(f"Vector directory : {result['vector_directory']}")

    print("\nDone.")


if __name__ == "__main__":
    main()
