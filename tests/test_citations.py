"""
test_citations.py - Production Tests for Reliable Document Retrieval & Citations

Verifies:
  1. Correct find command citations (https://tldr.sh/linux/find, excludes grep).
  2. Correct grep command citations (excludes find).
  3. Missing source metadata fallback handling.
  4. Empty retrieval results handling.
  5. Duplicate source URLs deduplication.
  6. Invalid URLs filtering.
  7. Irrelevant retrieved documents filtering.
  8. FastAPI response schema compliance.
  9. Streamlit citation rendering helpers.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.rag import answer_with_rag, extract_relevant_sources, is_valid_source_url

client = TestClient(app)


def test_find_command_citations():
    """Asking about find command returns find source and never displays grep."""
    res = answer_with_rag("How do I find all Python files in Linux?", top_k=5)
    assert "find" in res["answer"].lower()
    assert "-type f" in res["answer"]
    assert len(res["sources"]) > 0
    assert "https://tldr.sh/linux/find" in res["sources"]
    assert not any("grep" in s.lower() for s in res["sources"])
    assert not any("ls" in s.lower() for s in res["sources"])


def test_grep_command_citations():
    """Asking about grep command returns grep source and never displays find."""
    res = answer_with_rag("How can I search for a pattern in files?", top_k=5)
    assert "grep" in res["answer"].lower()
    assert len(res["sources"]) > 0
    assert any("grep" in s.lower() for s in res["sources"])
    assert not any("find" in s.lower() for s in res["sources"])


def test_missing_source_metadata_fallback():
    """When source metadata is missing, falls back to canonical documentation URL."""
    fake_hits = [
        {"page": "find", "title": "Find files", "score": 0.85, "source": ""},
    ]
    sources = extract_relevant_sources(fake_hits, fake_hits[0], query="find files")
    assert sources == ["https://tldr.sh/linux/find"]


def test_empty_retrieval_results():
    """When no documents pass relevance threshold, sources list is empty."""
    res = answer_with_rag("What is the stock price of Apple today?")
    assert res["sources"] == []
    assert res["confidence"] == 0.0

    empty_srcs = extract_relevant_sources([], {})
    assert empty_srcs == []


def test_duplicate_source_urls():
    """Duplicate sources are deduplicated while preserving order."""
    fake_hits = [
        {"page": "tar", "title": "Extract 1", "score": 0.85, "source": "https://tldr.sh/linux/tar"},
        {"page": "tar", "title": "Extract 2", "score": 0.80, "source": "https://tldr.sh/linux/tar"},
        {"page": "tar", "title": "Extract 3", "score": 0.75, "source": "https://tldr.sh/linux/tar"},
    ]
    sources = extract_relevant_sources(fake_hits, fake_hits[0], query="tar")
    assert len(sources) == 1
    assert sources == ["https://tldr.sh/linux/tar"]


def test_invalid_urls_filtered():
    """Non-HTTP URLs and invalid strings are filtered out; valid URLs are preserved."""
    assert is_valid_source_url("https://tldr.sh/linux/find") is True
    assert is_valid_source_url("http://example.com/docs") is True
    assert is_valid_source_url("data/raw/tar.md") is True
    assert is_valid_source_url("") is False
    assert is_valid_source_url("invalid-url-string") is False
    assert is_valid_source_url("ftp://broken/url") is False
    assert is_valid_source_url(None) is False

    fake_hits = [
        {"page": "curl", "title": "Curl", "score": 0.9, "source": "invalid_junk_url"},
    ]
    sources = extract_relevant_sources(fake_hits, fake_hits[0], query="curl")
    # Missing/invalid source falls back to canonical valid url
    assert sources == ["https://tldr.sh/linux/curl"]


def test_irrelevant_retrieved_documents_filtered():
    """Noise hits for different commands retrieved with lower scores are filtered out."""
    primary = {
        "page": "find",
        "title": "Find all Python files",
        "score": 0.75,
        "source": "https://tldr.sh/linux/find",
    }
    noise1 = {
        "page": "ls",
        "title": "List files",
        "score": 0.39,
        "source": "https://tldr.sh/linux/ls",
    }
    noise2 = {
        "page": "grep",
        "title": "Search text",
        "score": 0.35,
        "source": "https://tldr.sh/linux/grep",
    }

    sources = extract_relevant_sources(
        [primary, noise1, noise2], primary, query="find python files"
    )
    assert sources == ["https://tldr.sh/linux/find"]
    assert "https://tldr.sh/linux/ls" not in sources
    assert "https://tldr.sh/linux/grep" not in sources


def test_fastapi_ask_response_schema():
    """POST /ask returns compliant schema and accurate citations."""
    resp = client.post(
        "/ask", json={"question": "How do I find all Python files in Linux?", "top_k": 3}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["question"] == "How do I find all Python files in Linux?"
    assert "find" in data["answer"].lower()
    assert "-type f" in data["answer"]
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    assert "https://tldr.sh/linux/find" in data["sources"]
    assert not any("grep" in s.lower() for s in data["sources"])
    assert "confidence" in data
    assert "token_usage" in data


def test_streamlit_citation_rendering():
    """Verify Streamlit app helper correctly defines render_citations."""
    import ui.app as app_ui

    assert hasattr(app_ui, "render_citations")
    assert callable(app_ui.render_citations)
