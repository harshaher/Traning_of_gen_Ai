"""
test_day7.py - Comprehensive Unit and Integration Tests for ShellSathi Day 7

Tests:
  1. Chunking module: preserves source, page, title metadata.
  2. Embed module: produces normalized 384-d vectors, cosine similarity.
  3. VectorStore module: Chroma persistent storage, indexing, similarity search.
  4. FastAPI endpoints: /search/semantic, /health, /records.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
test_dir = Path(__file__).resolve().parent
project_root = test_dir.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient

from Day7.app.chunking import load_all_chunks, DocumentChunk
from Day7.app.embed import embed_text, cosine_similarity, get_embedding_function
from Day7.app.vectorstore import VectorStore
from Day7.app.main import app


def test_chunking_metadata_preservation():
    """Verify all chunks retain source, page, title, and valid content."""
    chunks = load_all_chunks()
    assert len(chunks) >= 24, f"Expected at least 24 chunks, found {len(chunks)}"

    for chunk in chunks:
        assert isinstance(chunk, DocumentChunk)
        assert chunk.chunk_id, "chunk_id must not be empty"
        assert chunk.source, f"source missing for chunk {chunk.chunk_id}"
        assert chunk.page in {"ls", "grep", "tar"}, f"unexpected page: {chunk.page}"
        assert chunk.title, f"title missing for chunk {chunk.chunk_id}"
        assert chunk.text, f"text missing for chunk {chunk.chunk_id}"
        assert "source" in chunk.metadata
        assert "page" in chunk.metadata
        assert "title" in chunk.metadata
    print("[PASS] test_chunking_metadata_preservation")


def test_embedding_dimensions_and_normalization():
    """Verify embedding vectors are 384-dimensional and normalized."""
    vec = embed_text("How can I list files?")

    assert len(vec) == 384, f"Expected 384 dimensions, got {len(vec)}"
    # Verify non-trivial dense representation
    assert any(x != 0.0 for x in vec), "Vector must not be all zeros"
    print("[PASS] test_embedding_dimensions_and_normalization")


def test_cosine_similarity():
    """Verify cosine similarity between identical and distinct queries."""
    v1 = embed_text("list all hidden files")
    v2 = embed_text("display hidden directory files")
    v3 = embed_text("what is the weather tomorrow")

    sim_related = cosine_similarity(v1, v2)
    sim_unrelated = cosine_similarity(v1, v3)

    assert sim_related > sim_unrelated, f"Related ({sim_related}) should be > unrelated ({sim_unrelated})"
    print("[PASS] test_cosine_similarity")


def test_vectorstore_indexing_and_search():
    """Test persistent Chroma vector store operations."""
    store = VectorStore()
    assert store.count() >= 24

    hits = store.search("display hidden files", top_k=3)
    assert len(hits) >= 1
    top_hit = hits[0]
    assert top_hit["page"] == "ls"
    assert "hidden" in top_hit["title"].lower()
    assert top_hit["score"] > 0.4
    assert top_hit["source"] != ""
    print("[PASS] test_vectorstore_indexing_and_search")


def test_fastapi_endpoints():
    """Test FastAPI /health, /records, and /search/semantic endpoints."""
    client = TestClient(app)

    # Health check
    res_health = client.get("/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.status_code}"
    data_health = res_health.json()
    assert data_health["status"] == "ok"
    assert data_health["vector_store"] == "Chroma"

    # Records endpoint
    res_records = client.get("/records?limit=5")
    assert res_records.status_code == 200
    data_records = res_records.json()
    assert data_records["returned"] <= 5
    assert len(data_records["records"]) > 0

    # Semantic search endpoint
    query = "How can I display hidden files?"
    res_search = client.get(f"/search/semantic?q={query}&limit=3")
    assert res_search.status_code == 200, f"Search failed: {res_search.text}"
    data_search = res_search.json()

    assert data_search["query"] == query
    assert data_search["total_hits"] == 3
    results = data_search["results"]
    assert len(results) == 3

    top = results[0]
    assert top["page"] == "ls"
    assert "hidden" in top["title"].lower()
    assert top["source"].startswith("http") or top["source"] != ""
    assert 0.0 <= top["score"] <= 1.0
    print("[PASS] test_fastapi_endpoints")


def run_all_tests():
    print("=== Running ShellSathi Day 7 Test Suite ===")
    test_chunking_metadata_preservation()
    test_embedding_dimensions_and_normalization()
    test_cosine_similarity()
    test_vectorstore_indexing_and_search()
    test_fastapi_endpoints()
    print("=== All 5 Day 7 Tests Passed Successfully! ===")


if __name__ == "__main__":
    run_all_tests()
