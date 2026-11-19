"""
test_search.py - Unit Tests for Search Capabilities (Day 11 S1-B)

Tests:
  1. Searching for an existing Linux command using TF-IDF.
  2. Searching for unknown or non-matching queries.
  3. Validating the return structure and ranking properties.
  4. ChromaDB dense semantic vector search structure.
"""

from app.smart_search import search_records
from app.vectorstore import get_vector_store


def test_search_existing_linux_command():
    """Verify that searching for a known Linux command returns matching records."""
    results = search_records("list directory contents", limit=5)
    assert len(results) > 0

    commands = [r.get("command") for r in results]
    assert "ls" in commands or "find" in commands


def test_search_unknown_command_returns_empty():
    """Verify that gibberish or unknown queries return an empty list gracefully."""
    results = search_records("zzzz_unknown_nonexistent_command_987654321")
    assert results == []


def test_search_result_structure():
    """Verify that search results contain required scoring and command metadata."""
    results = search_records("permissions chmod", limit=3)
    assert len(results) > 0

    expected_keys = {"command", "description", "example_command", "score"}
    for hit in results:
        assert expected_keys.issubset(set(hit.keys()))
        assert isinstance(hit["score"], (int, float))
        assert hit["score"] > 0

    # Check score descending order
    scores = [hit["score"] for hit in results]
    assert scores == sorted(scores, reverse=True)


def test_search_empty_and_whitespace_query():
    """Verify that empty queries return empty lists without exceptions."""
    assert search_records("") == []
    assert search_records("    ") == []


def test_vectorstore_semantic_search_structure():
    """Verify that ChromaDB neural vector store returns properly formatted chunk hits."""
    store = get_vector_store()
    results = store.search("how to archive files", top_k=3)

    assert isinstance(results, list)
    if results:
        top_hit = results[0]
        assert "chunk_id" in top_hit
        assert "text" in top_hit
        assert "source" in top_hit
        assert "page" in top_hit
        assert "title" in top_hit
        assert "score" in top_hit
        assert isinstance(top_hit["score"], (int, float))
