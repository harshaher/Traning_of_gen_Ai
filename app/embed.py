"""
embed.py - Neural dense embeddings and cosine similarity using all-MiniLM-L6-v2
"""

import math
from typing import Any, Dict, List, Optional

try:
    import chromadb.utils.embedding_functions as ef
    _default_ef = ef.DefaultEmbeddingFunction()
except Exception:
    _default_ef = None


def get_embedding_function():
    """Return the official all-MiniLM-L6-v2 ONNX embedding function."""
    global _default_ef
    if _default_ef is None:
        import chromadb.utils.embedding_functions as ef
        _default_ef = ef.DefaultEmbeddingFunction()
    return _default_ef


def embed_text(text: str) -> List[float]:
    """Generate 384-dimensional embedding vector for single text."""
    embedder = get_embedding_function()
    vectors = embedder([text])
    return [round(float(v), 6) for v in vectors[0]]


def embed_documents(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
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


def semantic_search_chunks(query: str, chunks: List[Any], top_k: int = 5) -> List[Dict[str, Any]]:
    """Perform direct dense semantic search across document chunks."""
    if not query or not chunks:
        return []

    embedder = get_embedding_function()
    query_vector = embedder([query])[0]
    doc_texts = [chunk.text for chunk in chunks]
    doc_vectors = embedder(doc_texts)

    scored = []
    for chunk, doc_vec in zip(chunks, doc_vectors):
        score = cosine_similarity(query_vector, doc_vec)
        scored.append({
            "chunk_id": chunk.chunk_id,
            "score": score,
            "source": chunk.source,
            "page": chunk.page,
            "title": chunk.title,
            "text": chunk.text,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
