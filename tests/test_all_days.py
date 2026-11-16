"""
test_all_days.py - Comprehensive Unit & Integration Test Suite
Verifies all capabilities from Day 1 to Day 9 for ShellSathi:
  - Day 1: Interactive flow logic and command recommendations.
  - Day 2: 20 Linux commands, records loading, filtering, search, and destructive checks.
  - Day 3: Ingestion pipeline, Record model dataclass, and markdown parsing.
  - Day 4: TF-IDF Smart Search and core FastAPI REST endpoints.
  - Day 5: Out-of-scope boundaries and honest 'I don't know' responses.
  - Day 6: LLM integration with structured JSON schema (answer, confidence, follow_up).
  - Day 7: Dense neural embeddings and semantic search via ChromaDB vector store.
  - Day 8: RAG retrieval-augmented generation with verified source citations.
  - Day 9: Chmod calculator tool, safety interceptors, LangGraph agent workflow, and /agent endpoint.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient

from app.models import Record, DocumentChunk
from app.records import (
    load_records,
    get_by_id,
    search,
    count_by,
)
from app.tools import chmod_calculator, check_destructive_command
from app.smart_search import search_records
from app.vectorstore import get_vector_store
from app.rag import answer_with_rag, is_out_of_scope
from app.graph import run_graph
from app.agent_loop import run_agent
from app.main import app

client = TestClient(app)


# ==========================================
# DAY 1 & 2: Command Records & Logic
# ==========================================

def test_day2_records_count_and_content():
    """Verify that records.json contains at least 20 unique Linux commands."""
    records = load_records()
    assert len(records) >= 20, f"Expected >= 20 records, got {len(records)}"

    unique_commands = {r.get("command") for r in records if r.get("command")}
    assert len(unique_commands) >= 20, f"Expected 20 unique commands, got {len(unique_commands)}"

    expected_sample = {"ls", "grep", "tar", "chmod", "curl", "find", "systemctl", "ssh"}
    for cmd in expected_sample:
        assert cmd in unique_commands, f"Expected command '{cmd}' missing from records"


def test_day2_record_functions():
    """Test get_by_id, search, count_by, and destructive check."""
    records = load_records()
    rec = get_by_id(records, 1)
    assert rec is not None
    assert "command" in rec

    results = search(records, "list")
    assert len(results) > 0

    counts = count_by(records, "category")
    assert len(counts) > 0

    safety_destr = check_destructive_command("rm -rf /var/log")
    assert safety_destr["destructive"] is True
    assert "delete" in safety_destr["warning"].lower() or "destructive" in safety_destr["warning"].lower()

    safety_safe = check_destructive_command("ls -la")
    assert safety_safe["destructive"] is False


# ==========================================
# DAY 3: Models & Ingestion
# ==========================================

def test_day3_dataclass_models():
    """Test Record and DocumentChunk dataclass models."""
    r = Record(
        command="find",
        platform="linux",
        description="Search for files in directory hierarchy",
        example_task="Find files by name",
        example_command="find . -name '*.py'",
        source_url="https://example.com/find.md",
    )
    assert r.command == "find"
    d = r.to_dict()
    assert d["command"] == "find"
    assert d["example_task"] == "Find files by name"

    chunk = DocumentChunk(
        chunk_id="chunk_01",
        page="find",
        title="Find files by name",
        source="https://example.com/find.md",
        text="Sample text",
    )
    assert chunk.chunk_id == "chunk_01"
    cd = chunk.to_dict()
    assert cd["page"] == "find"
    assert cd["metadata"]["title"] == "Find files by name"


# ==========================================
# DAY 4: TF-IDF Search & REST API
# ==========================================

def test_day4_smart_search_tfidf():
    """Verify TF-IDF search returns relevant results."""
    hits = search_records("search pattern in files", limit=3)
    assert len(hits) > 0
    top_hit = hits[0]
    assert "grep" in top_hit.get("command", "").lower() or "grep" in top_hit.get("example_task", "").lower()


def test_day4_fastapi_base_endpoints():
    """Verify GET /health, /records, /records/{id}, /search, and POST /questions."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["indexed_chunks"] >= 20

    r = client.get("/records")
    assert r.status_code == 200
    assert r.json()["total"] >= 20

    r = client.get("/records/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1

    r = client.get("/search?q=tar")
    assert r.status_code == 200
    assert len(r.json()["results"]) > 0

    payload = {"question": "How to extract tar file?"}
    r = client.post("/questions", json=payload)
    assert r.status_code == 200
    assert "results" in r.json()


# ==========================================
# DAY 5: Out of Scope & Boundaries
# ==========================================

def test_day5_out_of_scope_boundary():
    """Verify Q6 (weather / VPN queries) are recognized as out-of-scope."""
    assert is_out_of_scope("What will the weather be tomorrow?") is True
    assert is_out_of_scope("Why is our company VPN slow from the Hinjewadi office today?") is True
    assert is_out_of_scope("How to list files using ls?") is False


# ==========================================
# DAY 6: LLM & Chat Endpoint
# ==========================================

def test_day6_chat_endpoint_schema():
    """POST /chat must return JSON containing answer, confidence, follow_up."""
    payload = {"message": "How do I list hidden files?"}
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "confidence" in data
    assert "follow_up" in data
    assert isinstance(data["confidence"], (int, float))
    assert 0.0 <= data["confidence"] <= 1.0


# ==========================================
# DAY 7: Semantic Search & Vectorstore
# ==========================================

def test_day7_semantic_search():
    """GET /search/semantic?q= must return hits from ChromaDB."""
    r = client.get("/search/semantic?q=list files in long format")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert "ls" in top["page"].lower()
    assert "source" in top
    assert "title" in top


# ==========================================
# DAY 8: RAG Endpoint & Retrieval
# ==========================================

def test_day8_rag_ask_in_scope():
    """POST /ask returns answer with verified source citations."""
    payload = {"question": "How can I search for a pattern in files?"}
    r = client.post("/ask", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "grep" in data["answer"].lower()
    assert len(data["sources"]) > 0
    assert data["confidence"] > 0.0


def test_day8_rag_ask_out_of_scope_q6():
    """POST /ask for Q6 returns an honest 'I don't know' with zero sources."""
    payload = {"question": "Why is our company VPN slow from the Hinjewadi office today?"}
    r = client.post("/ask", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "don't know" in data["answer"].lower()
    assert data["sources"] == []
    assert data["confidence"] == 0.0


# ==========================================
# DAY 9: Tools, Agent Loop, LangGraph, /agent
# ==========================================

def test_day9_chmod_calculator_octal():
    """Test octal to symbolic and entity breakdown."""
    res = chmod_calculator("755")
    assert res["valid"] is True
    assert res["symbolic"] == "rwxr-xr-x"
    assert "breakdown" in res
    assert res["breakdown"]["owner"]["read"] is True


def test_day9_chmod_calculator_symbolic():
    """Test symbolic to octal conversion."""
    res = chmod_calculator("rwxr-xr-x")
    assert res["valid"] is True
    assert res["octal"] == "755"


def test_day9_chmod_calculator_invalid():
    """Test invalid permission input rejection."""
    res = chmod_calculator("999")
    assert res["valid"] is False
    assert "error" in res


def test_day9_agent_loop_tool_routing():
    """Hand-written agent loop routes chmod queries to chmod calculator."""
    res = run_agent("What does chmod 644 mean?")
    assert "chmod_calculator" in res["tools_used"]
    assert "rw-r--r--" in res["answer"]


def test_day9_langgraph_workflow_safe():
    """LangGraph workflow executes and provides status."""
    result = run_graph("How to compress files with tar?")
    assert result["intent"] == "rag"
    assert "tar" in result["answer"].lower()


def test_day9_langgraph_workflow_destructive_approval():
    """LangGraph workflow blocks destructive command when not approved."""
    result = run_graph("Run rm -rf /var/log to clear space", approved=False)
    assert result["intent"] == "approval"
    assert result["approval_required"] is True


def test_day9_agent_endpoint():
    """POST /agent handles routing, tools, and human approval."""
    payload = {"question": "Convert chmod 755 to symbolic"}
    r = client.post("/agent", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "chmod_calculator" in data["tools_used"]
    assert "rwxr-xr-x" in data["answer"]


def test_day9_agent_endpoint_destructive():
    """POST /agent detects destructive commands."""
    payload = {"question": "rm -rf /important_files", "approved": False}
    r = client.post("/agent", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["approval_required"] is True


if __name__ == "__main__":
    pytest.main(["-v", __file__])
