"""
vectorstore.py - Persistent Chroma vector database for ShellSathi
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

from app.chunking import DocumentChunk, load_all_chunks
from app.embed import get_embedding_function

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PERSIST_DIR = PROJECT_ROOT / "data" / "chroma_db"
DEFAULT_COLLECTION = "shellsathi_knowledge"


class VectorStore:
    """Manages persistent Chroma vector database."""

    def __init__(
        self, persist_dir: Optional[Path] = None, collection_name: str = DEFAULT_COLLECTION
    ):
        self.persist_dir = persist_dir or DEFAULT_PERSIST_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.embedding_fn = get_embedding_function()

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection.count()

    def index_chunks(
        self, chunks: Optional[List[DocumentChunk]] = None, force: bool = False
    ) -> int:
        """Index chunks into persistent collection."""
        curr = self.collection.count()
        if curr > 0 and not force:
            return curr

        chunk_list = chunks or load_all_chunks()
        if not chunk_list:
            return 0

        if force and curr > 0:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )

        ids = [c.chunk_id for c in chunk_list]
        docs = [c.text for c in chunk_list]
        metas = [c.metadata for c in chunk_list]

        self.collection.upsert(ids=ids, documents=docs, metadatas=metas)
        return self.collection.count()

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search Chroma collection using cosine semantic similarity."""
        if not query or not query.strip():
            return []

        if self.collection.count() == 0:
            self.index_chunks()

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits = []
        if not results or not results["ids"] or not results["ids"][0]:
            return hits

        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

        for rank, (cid, doc, meta, dist) in enumerate(zip(ids, docs, metas, distances), start=1):
            score = max(0.0, min(1.0, round(1.0 - float(dist), 4)))
            hits.append(
                {
                    "rank": rank,
                    "chunk_id": cid,
                    "score": score,
                    "distance": round(float(dist), 4),
                    "source": meta.get("source", ""),
                    "page": meta.get("page", ""),
                    "title": meta.get("title", ""),
                    "text": doc,
                }
            )

        return hits


_global_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Return singleton vector store instance."""
    global _global_vector_store
    if _global_vector_store is None:
        _global_vector_store = VectorStore()
        if _global_vector_store.count() == 0:
            _global_vector_store.index_chunks()
    return _global_vector_store
