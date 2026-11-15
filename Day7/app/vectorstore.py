"""
vectorstore.py - ShellSathi Chroma Vector Store Module

Indexes document chunks into a persistent Chroma collection and performs
fast, accurate semantic similarity search.

Preserves chunk metadata:
  - source: Document source / upstream URL
  - page: Command name (e.g. ls, grep, tar)
  - title: Command operation title
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

try:
    from Day7.app.chunking import DocumentChunk, load_all_chunks
    from Day7.app.embed import get_embedding_function
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from Day7.app.chunking import DocumentChunk, load_all_chunks
    from Day7.app.embed import get_embedding_function

logger = logging.getLogger("shellsathi.vectorstore")

DEFAULT_COLLECTION_NAME = "shellsathi_chunks"


class VectorStore:
    """Manages persistent Chroma vector database for ShellSathi."""

    def __init__(
        self,
        persist_directory: Optional[Path | str] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ):
        if persist_directory is None:
            base_dir = Path(__file__).resolve().parent.parent
            self.persist_directory = base_dir / "data" / "chroma"
        else:
            self.persist_directory = Path(persist_directory)

        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_fn = get_embedding_function()

        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        """Return total number of chunks currently indexed in Chroma."""
        return self.collection.count()

    def index_chunks(
        self,
        chunks: Optional[List[DocumentChunk]] = None,
        force_reindex: bool = False,
    ) -> int:
        """
        Index all chunks into Chroma vector store.
        Skips indexing if chunks are already present unless force_reindex=True.
        """
        current_count = self.collection.count()
        if current_count > 0 and not force_reindex:
            logger.info("Chroma already indexed with %d chunks. Skipping reindex.", current_count)
            return current_count

        if chunks is None:
            chunks = load_all_chunks()

        if not chunks:
            logger.warning("No chunks found to index.")
            return 0

        if force_reindex and current_count > 0:
            # Delete existing collection and recreate
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )

        ids = [c.chunk_id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        # Chroma upsert ensures idempotency
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        total = self.collection.count()
        logger.info("Indexed %d chunks into persistent Chroma collection '%s'.", total, self.collection_name)
        return total

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search against the Chroma index.
        Returns top_k ranked results with source, page, title, and similarity score.
        """
        if not query or not query.strip():
            return []

        # Auto-index if collection is empty
        if self.collection.count() == 0:
            self.index_chunks()

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: List[Dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return hits

        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

        for rank, (chunk_id, doc, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
            # Chroma cosine distance: distance = 1 - cosine_similarity
            similarity_score = max(0.0, min(1.0, round(1.0 - float(dist), 4)))
            hits.append(
                {
                    "rank": rank,
                    "chunk_id": chunk_id,
                    "score": similarity_score,
                    "distance": round(float(dist), 4),
                    "source": meta.get("source", ""),
                    "page": meta.get("page", ""),
                    "title": meta.get("title", ""),
                    "text": doc,
                }
            )

        return hits


# Global singleton instance for FastAPI application
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Return singleton VectorStore instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
        if _vector_store.count() == 0:
            _vector_store.index_chunks()
    return _vector_store


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

    store = VectorStore()
    count = store.index_chunks(force_reindex=True)
    print(f"Persistent Chroma index ready with {count} chunks.")

    test_query = "How can I display hidden files?"
    results = store.search(test_query, top_k=3)
    print(f"\nQuery: {test_query}")
    for hit in results:
        print(f"Rank {hit['rank']}: [{hit['score']:.4f}] {hit['page']} -> {hit['title']} (ID: {hit['chunk_id']})")
        print(f"  Source: {hit['source']}")
