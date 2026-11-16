"""
embed.py - ShellSathi Embedding and Semantic Search Module

Provides dense vector embeddings and semantic search functionality:
  - Uses Chroma's official DefaultEmbeddingFunction (all-MiniLM-L6-v2, 384 dimensions).
  - Plugs into persistent Chroma vector collections.
  - Supports query embedding, document embedding, and cosine similarity scoring.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

try:
    import chromadb.utils.embedding_functions as ef
    _default_ef = ef.DefaultEmbeddingFunction()
except Exception:
    _default_ef = None


def get_embedding_function():
    """
    Return the active Chroma-compatible embedding function.
    Uses official all-MiniLM-L6-v2 ONNX embedding function.
    """
    global _default_ef
    if _default_ef is None:
        import chromadb.utils.embedding_functions as ef
        _default_ef = ef.DefaultEmbeddingFunction()
    return _default_ef


def embed_text(text: str) -> List[float]:
    """Generate a 384-dimensional embedding vector for a single string."""
    embedder = get_embedding_function()
    vectors = embedder([text])
    return [round(float(v), 6) for v in vectors[0]]


def embed_documents(texts: List[str]) -> List[List[float]]:
    """Generate dense embeddings for a batch of documents."""
    if not texts:
        return []
    embedder = get_embedding_function()
    vectors = embedder(texts)
    return [[round(float(v), 6) for v in vec] for vec in vectors]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two dense vectors."""
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same dimension")

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return round(dot / (norm1 * norm2), 4)


def semantic_search_chunks(
    query: str,
    chunks: List[Any],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Perform semantic similarity search across an iterable of DocumentChunk objects
    using dense embeddings and cosine similarity scoring.
    """
    if not query or not chunks:
        return []

    embedder = get_embedding_function()
    query_vector = embedder([query])[0]
    doc_texts = [chunk.text for chunk in chunks]
    doc_vectors = embedder(doc_texts)

    scored_results = []
    for chunk, doc_vec in zip(chunks, doc_vectors):
        score = cosine_similarity(query_vector, doc_vec)
        scored_results.append(
            {
                "chunk_id": chunk.chunk_id,
                "score": score,
                "source": chunk.source,
                "page": chunk.page,
                "title": chunk.title,
                "text": chunk.text,
            }
        )

    # Sort descending by score
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:top_k]


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from Day7.app.chunking import load_all_chunks

    test_chunks = load_all_chunks()
    q = "How can I display hidden files?"
    results = semantic_search_chunks(q, test_chunks, top_k=3)
    print(f"Query: {q}")
    for rank, r in enumerate(results, 1):
        print(f"{rank}. [{r['score']:.4f}] {r['page']} - {r['title']} (ID: {r['chunk_id']})")
