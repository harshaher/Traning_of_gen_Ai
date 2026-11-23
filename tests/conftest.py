"""
conftest.py - Pytest Fixtures and Mock Providers for ShellSathi Test Suite

Provides:
  - Reusable FastAPI TestClient fixture.
  - Mock LLM / RAG response generators (zero external API calls / zero paid keys).
  - Mock LLM failure simulators for error handling tests.
  - Temporary feedback storage fixture to preserve production records.
  - Sample Linux command records and document chunks.
"""

from pathlib import Path
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import DocumentChunk, Record


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_record() -> Record:
    """Provide a valid Linux command Record instance."""
    return Record(
        command="grep",
        platform="linux",
        description="Search for patterns in files using regular expressions",
        example_task="Search for an exact string in a file",
        example_command="grep -F 'pattern' file.txt",
        source_url="https://github.com/tldr-pages/tldr/blob/main/pages/common/grep.md",
    )


@pytest.fixture
def sample_chunk() -> DocumentChunk:
    """Provide a valid DocumentChunk instance."""
    return DocumentChunk(
        chunk_id="chunk_test_01",
        text="Give the user who owns a file the right to execute it: chmod u+x {{path/to/file}}",
        source="data/raw/chmod.md",
        page="chmod",
        title="Execute permission for user",
    )


@pytest.fixture
def fake_rag_response() -> Dict[str, Any]:
    """Deterministic fake RAG response without external network calls."""
    return {
        "question": "How do I extract a tar archive?",
        "answer": "To extract an archive, use: `tar -xvf {{archive.tar.gz}} -C {{target_dir}}`",
        "sources": ["data/raw/tar.md"],
        "confidence": 0.95,
        "context_used": ["[tar] Extract an archive: tar -xvf {{archive.tar.gz}}"],
    }


@pytest.fixture
def mock_llm_ask(monkeypatch: pytest.MonkeyPatch, fake_rag_response: Dict[str, Any]) -> None:
    """
    Monkeypatch answer_with_rag in app.main to return a deterministic fake RAG answer.
    Guarantees no real external API calls or API keys are required during testing.
    """

    def _fake_answer_with_rag(question: str, top_k: int = 3) -> Dict[str, Any]:
        resp = dict(fake_rag_response)
        resp["question"] = question
        return resp

    monkeypatch.setattr("app.main.answer_with_rag", _fake_answer_with_rag)


@pytest.fixture
def mock_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Monkeypatch answer_with_rag in app.main to simulate an upstream LLM/provider failure.
    """

    def _failing_answer_with_rag(question: str, top_k: int = 3) -> Dict[str, Any]:
        raise RuntimeError("Simulated upstream LLM provider connection error")

    monkeypatch.setattr("app.main.answer_with_rag", _failing_answer_with_rag)


@pytest.fixture
def mock_chat_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Monkeypatch generate_answer in app.main for POST /chat tests.
    """

    def _fake_generate_answer(prompt: str) -> str:
        return '{"answer": "Use `chmod 755 file`.", "confidence": 0.92, "follow_up": "Do you need symbolic mode?"}'

    monkeypatch.setattr("app.main.generate_answer", _fake_generate_answer)


@pytest.fixture
def temp_feedback_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect FEEDBACK_FILE in app.main to an isolated temporary JSON file."""
    temp_file = tmp_path / "feedback.json"
    temp_file.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("app.main.FEEDBACK_FILE", temp_file)
    return temp_file
