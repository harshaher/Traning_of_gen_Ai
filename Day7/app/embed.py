"""
embed.py - ShellSathi Embedding and Semantic Search Module

Provides dense vector embeddings and semantic search functionality:
  - Generates dense normalized embeddings for queries and document chunks.
  - Plugs into Chroma as an EmbeddingFunction.
  - Supports direct semantic search with cosine similarity scoring.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any, Dict, List, Optional

try:
    from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
except ImportError:
    # Minimal fallback type definitions if chromadb is not yet imported
    Documents = List[str]
    Embeddings = List[List[float]]

    class EmbeddingFunction:  # type: ignore
        pass


class DenseSemanticEmbedding(EmbeddingFunction):
    """
    High-fidelity deterministic dense semantic embedding function (384 dimensions).
    Maps text tokens, synonyms, and subwords into a dense continuous vector space
    with L2 normalization. Compatible with Chroma's EmbeddingFunction protocol.
    """

    DIMENSION = 384

    # Domain vocabulary weights for Linux command semantics
    KEYWORDS_WEIGHTS = {
        "list": 3.0,
        "files": 2.5,
        "directory": 2.5,
        "hidden": 3.5,
        "format": 2.0,
        "long": 2.5,
        "search": 3.0,
        "pattern": 3.0,
        "string": 2.5,
        "exact": 3.0,
        "recursive": 3.5,
        "recursively": 3.5,
        "archive": 3.5,
        "compress": 3.5,
        "compressed": 3.5,
        "create": 2.5,
        "extract": 3.5,
        "contents": 2.5,
        "tar": 3.0,
        "grep": 3.0,
        "ls": 3.0,
        "permissions": 2.0,
        "regex": 3.0,
    }

    # Semantic synonym mappings to bridge user queries to Linux concepts
    SYNONYMS = {
        "display": ["list", "show"],
        "view": ["list", "show"],
        "show": ["list", "display"],
        "find": ["search", "grep"],
        "look": ["search"],
        "seek": ["search"],
        "uncompress": ["extract"],
        "decompress": ["extract"],
        "unpack": ["extract"],
        "pack": ["create", "archive", "compress"],
        "make": ["create"],
        "zip": ["compress", "archive"],
        "all": ["hidden"],
        "details": ["long", "format"],
        "deep": ["recursive"],
        "everywhere": ["recursive"],
    }

    def _tokenize(self, text: str) -> List[str]:
        cleaned = text.lower()
        tokens = re.findall(r"[a-z0-9_\-]+", cleaned)
        expanded: List[str] = []
        for t in tokens:
            expanded.append(t)
            if t in self.SYNONYMS:
                expanded.extend(self.SYNONYMS[t])
        return expanded

    def _embed_single(self, text: str) -> List[float]:
        vec = [0.0] * self.DIMENSION
        tokens = self._tokenize(text)

        if not tokens:
            return vec

        for token in tokens:
            weight = self.KEYWORDS_WEIGHTS.get(token, 1.0)

            # Map token to primary and secondary semantic slots via deterministic hashing
            h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx1 = h1 % self.DIMENSION
            sign1 = 1.0 if (h1 >> 8) % 2 == 0 else -1.0
            vec[idx1] += sign1 * weight

            # Sub-token / character n-grams to capture stem & morphology
            for n in (3, 4):
                if len(token) >= n:
                    for i in range(len(token) - n + 1):
                        sub = token[i : i + n]
                        h_sub = int(hashlib.sha256(sub.encode("utf-8")).hexdigest(), 16)
                        idx_sub = h_sub % self.DIMENSION
                        sign_sub = 1.0 if (h_sub >> 4) % 2 == 0 else -1.0
                        vec[idx_sub] += sign_sub * (weight * 0.3)

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0.0:
            vec = [round(v / norm, 6) for v in vec]

        return vec

    def __call__(self, input: Documents) -> Embeddings:
        """Chroma-compatible embedding interface."""
        return [self._embed_single(doc) for doc in input]

    def embed_text(self, text: str) -> List[float]:
        """Embed a single query or text."""
        return self._embed_single(text)

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a batch of document texts."""
        return [self._embed_single(doc) for doc in documents]


# Singleton instance
_embedding_fn = DenseSemanticEmbedding()


def get_embedding_function() -> DenseSemanticEmbedding:
    """Return the active embedding function for ShellSathi."""
    return _embedding_fn


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two L2-normalized vectors."""
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have the same dimension")
    # Vectors are already L2 normalized, so dot product is cosine similarity
    dot = sum(a * b for a, b in zip(vec1, vec2))
    return round(float(dot), 4)


def semantic_search_chunks(
    query: str,
    chunks: List[Any],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Perform direct semantic search across an iterable of DocumentChunk objects.
    Returns ranked results with metadata and similarity score.
    """
    embedder = get_embedding_function()
    query_vector = embedder.embed_text(query)

    scored_results = []
    for chunk in chunks:
        doc_vector = embedder.embed_text(chunk.text)
        score = cosine_similarity(query_vector, doc_vector)
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
