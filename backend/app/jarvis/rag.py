from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import chromadb
import fitz
from sentence_transformers import SentenceTransformer


class RAGDocument:
    def __init__(
        self,
        text: str,
        source: str,
        page: int,
        chunk_id: str,
    ):
        self.text = text
        self.source = source
        self.page = page
        self.chunk_id = chunk_id


class TeddyRAG:
    """
    Retrieval-Augmented Generation knowledge layer for Teddy.

    Responsibilities:
    1. Load Hadoop knowledge documents.
    2. Extract text.
    3. Split text into chunks.
    4. Generate embeddings.
    5. Store embeddings in ChromaDB.
    6. Retrieve relevant Hadoop knowledge for a question.
    """

    def __init__(
        self,
        knowledge_dir: str | None = None,
        vector_dir: str | None = None,
        embedding_model: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        top_k: int | None = None,
    ):
        self.knowledge_dir = Path(
            knowledge_dir
            or os.getenv("RAG_KNOWLEDGE_DIR", "data/knowledge")
        )

        self.vector_dir = Path(
            vector_dir
            or os.getenv("RAG_VECTOR_DIR", "data/chroma")
        )

        self.embedding_model_name = (
            embedding_model
            or os.getenv(
                "RAG_EMBEDDING_MODEL",
                "all-MiniLM-L6-v2",
            )
        )

        self.chunk_size = int(
            chunk_size
            or os.getenv("RAG_CHUNK_SIZE", "1200")
        )

        self.chunk_overlap = int(
            chunk_overlap
            or os.getenv("RAG_CHUNK_OVERLAP", "200")
        )

        self.top_k = int(
            top_k
            or os.getenv("RAG_TOP_K", "5")
        )

        self.vector_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.embedding_model = SentenceTransformer(
            self.embedding_model_name
        )

        self.client = chromadb.PersistentClient(
            path=str(self.vector_dir)
        )

        self.collection = self.client.get_or_create_collection(
            name="teddy_hadoop_knowledge"
        )

        try:
            if self.collection.count() == 0:
                print("[TeddyRAG] Initializing RAG vector store index from PDF knowledge...")
                self.build_index()
        except Exception as e:
            print(f"[TeddyRAG] Auto-index notice: {e}")

    # ---------------------------------------------------------
    # DOCUMENT LOADING
    # ---------------------------------------------------------

    def load_documents(self) -> list[RAGDocument]:
        documents: list[RAGDocument] = []

        pdf_files = list(
            self.knowledge_dir.glob("*.pdf")
        )

        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in {self.knowledge_dir}"
            )

        for pdf_path in pdf_files:
            pdf = fitz.open(pdf_path)

            for page_number, page in enumerate(
                pdf,
                start=1,
            ):
                text = page.get_text("text").strip()

                if not text:
                    continue

                chunks = self._chunk_text(text)

                for index, chunk in enumerate(chunks):
                    chunk_id = (
                        f"{pdf_path.stem}"
                        f"_p{page_number}"
                        f"_c{index}"
                    )

                    documents.append(
                        RAGDocument(
                            text=chunk,
                            source=pdf_path.name,
                            page=page_number,
                            chunk_id=chunk_id,
                        )
                    )

            pdf.close()

        return documents

    # ---------------------------------------------------------
    # CHUNKING
    # ---------------------------------------------------------

    def _chunk_text(self, text: str) -> list[str]:
        text = " ".join(text.split())

        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []

        start = 0

        while start < len(text):
            end = start + self.chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            next_start = end - self.chunk_overlap

            if next_start <= start:
                break

            start = next_start

        return chunks

    # ---------------------------------------------------------
    # INDEXING
    # ---------------------------------------------------------

    def build_index(self) -> dict[str, Any]:
        documents = self.load_documents()

        if not documents:
            raise RuntimeError(
                "No usable knowledge was extracted."
            )

        texts = [
            document.text
            for document in documents
        ]

        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        ids = [
            document.chunk_id
            for document in documents
        ]

        metadatas = [
            {
                "source": document.source,
                "page": document.page,
            }
            for document in documents
        ]

        # Rebuild collection so indexing is deterministic.
        try:
            self.client.delete_collection(
                "teddy_hadoop_knowledge"
            )
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name="teddy_hadoop_knowledge"
        )

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
        )

        return {
            "documents": len(documents),
            "collection": "teddy_hadoop_knowledge",
            "embedding_model": self.embedding_model_name,
            "vector_directory": str(
                self.vector_dir
            ),
        }

    # ---------------------------------------------------------
    # RETRIEVAL
    # ---------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:

        if not query.strip():
            return []

        count = top_k or self.top_k

        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
        )

        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=count,
        )

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        retrieved = []

        for index, document in enumerate(documents):
            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            retrieved.append(
                {
                    "text": document,
                    "source": metadata.get(
                        "source"
                    ),
                    "page": metadata.get(
                        "page"
                    ),
                    "distance": distance,
                }
            )

        return retrieved

    # ---------------------------------------------------------
    # CONTEXT BUILDING
    # ---------------------------------------------------------

    def build_context(
        self,
        query: str,
        top_k: int | None = None,
    ) -> str:

        results = self.retrieve(
            query=query,
            top_k=top_k,
        )

        if not results:
            return ""

        context_parts = []

        for result in results:
            context_parts.append(
                (
                    f"[Source: {result['source']}, "
                    f"Page: {result['page']}]\n"
                    f"{result['text']}"
                )
            )

        return "\n\n---\n\n".join(
            context_parts
        )


# Backward compatibility alias for legacy orchestrator imports
LocalRAG = TeddyRAG

