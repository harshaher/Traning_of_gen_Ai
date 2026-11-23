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
  - Day 9: chmod calculator tool, hand-written agent loop, LangGraph workflow with memory and approval, and /agent endpoint.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient

from app.agent_loop import run_agent_loop
from app.graph import run_graph
from app.main import app
from app.models import DocumentChunk, Record
from app.placeholder import (
    extract_placeholders,
    fill_template,
    find_command_templates,
    has_placeholders,
)
from app.rag import is_out_of_scope
from app.records import (
    count_by,
    get_by_id,
    load_records,
    search,
)
from app.smart_search import search_records
from app.tools import check_destructive_command, chmod_calculator

client = TestClient(app)


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
    assert (
        "delete" in safety_destr["warning"].lower()
        or "destructive" in safety_destr["warning"].lower()
    )

    safety_safe = check_destructive_command("ls -la")
    assert safety_safe["destructive"] is False


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


def test_day4_smart_search_tfidf():
    """Verify TF-IDF search returns relevant results."""
    hits = search_records("search pattern in files", limit=3)
    assert len(hits) > 0
    top_hit = hits[0]
    assert (
        "grep" in top_hit.get("command", "").lower()
        or "grep" in top_hit.get("example_task", "").lower()
    )


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


def test_day5_out_of_scope_boundary():
    """Verify Q6 (weather / VPN queries) are recognized as out-of-scope."""
    assert is_out_of_scope("What will the weather be tomorrow?") is True
    assert is_out_of_scope("Why is our company VPN slow from the Hinjewadi office today?") is True
    assert is_out_of_scope("How to list files using ls?") is False


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


def test_day9_chmod_conversions_all_required():
    """Test all 6 target permission conversions in both directions."""
    c1 = chmod_calculator("rwxr-x---")
    assert c1["valid"] is True and c1["converted_permission"] == "750"
    assert "read, write, execute" in c1["owner_permissions"]
    assert "read, execute" in c1["group_permissions"]
    assert "no permissions" in c1["others_permissions"]

    c2 = chmod_calculator("rwxr-xr-x")
    assert c2["valid"] is True and c2["converted_permission"] == "755"

    c3 = chmod_calculator("rw-------")
    assert c3["valid"] is True and c3["converted_permission"] == "600"

    c4 = chmod_calculator("750")
    assert c4["valid"] is True and c4["converted_permission"] == "rwxr-x---"

    c5 = chmod_calculator("755")
    assert c5["valid"] is True and c5["converted_permission"] == "rwxr-xr-x"

    c6 = chmod_calculator("600")
    assert c6["valid"] is True and c6["converted_permission"] == "rw-------"


def test_day9_chmod_validation_errors():
    """Test validation of invalid symbolic, invalid octal, and empty inputs."""
    e1 = chmod_calculator("rwxr-x--z")
    assert e1["valid"] is False
    assert "error" in e1

    e2 = chmod_calculator("899")
    assert e2["valid"] is False
    assert "error" in e2

    e3 = chmod_calculator("")
    assert e3["valid"] is False
    assert "error" in e3

    e4 = chmod_calculator(None)
    assert e4["valid"] is False
    assert "error" in e4

    e5 = chmod_calculator("75")
    assert e5["valid"] is False


def test_day9_agent_loop_rag_selection():
    """Agent loop selects RAG search for general command queries."""
    res = run_agent_loop("How can I find a file named test.txt in Linux?")
    assert res["tool_used"] == "rag_search"
    assert "tools_used" in res
    assert len(res["sources"]) > 0


def test_day9_agent_loop_chmod_selection():
    """Agent loop selects chmod_calculator for permission queries."""
    res = run_agent_loop("Convert rwxr-x--- into octal.")
    assert res["tool_used"] == "chmod_calculator"
    assert "750" in res["answer"]
    assert "owner" in res["answer"].lower()


def test_day9_agent_loop_octal_explanation():
    """Agent loop explains octal permission 755."""
    res = run_agent_loop("What does chmod 755 mean?")
    assert res["tool_used"] == "chmod_calculator"
    assert "rwxr-xr-x" in res["answer"]


def test_day9_agent_loop_unknown_question():
    """Agent loop honestly refuses out-of-scope VPN question."""
    res = run_agent_loop("Why is our company VPN slow from the Hinjewadi office today?")
    assert "don't know" in res["answer"].lower()
    assert res["sources"] == []


def test_day9_agent_loop_empty_query():
    """Agent loop safely handles empty input."""
    res = run_agent_loop("")
    assert "please provide" in res["answer"].lower()


def test_day9_langgraph_rag_execution():
    """LangGraph workflow executes safe RAG query without pausing for approval."""
    res = run_graph("How can I search for files in Linux?", thread_id="test_lg_rag")
    assert res["tool_used"] == "rag_search"
    assert "answer" in res
    assert res["approval_required"] is False
    assert res["status"] == "COMPLETED"


def test_day9_langgraph_chmod_approval_and_rejection():
    """LangGraph pauses for chmod approval, then handles rejection."""
    res_pause = run_graph("Convert rwxr-x--- into octal", thread_id="test_lg_rej")
    assert res_pause["approval_required"] is True
    assert res_pause["status"] == "PENDING_APPROVAL"

    res_rej = run_graph("", approved=False, thread_id="test_lg_rej")
    assert res_rej["approval_required"] is False
    assert "rejected" in res_rej["answer"].lower()
    assert res_rej["status"] == "REJECTED"


def test_day9_langgraph_chmod_approval_and_success():
    """LangGraph pauses for chmod approval, then executes upon approval."""
    res_pause = run_graph("Convert rwxr-x--- into octal", thread_id="test_lg_appr")
    assert res_pause["approval_required"] is True

    res_ok = run_graph("", approved=True, thread_id="test_lg_appr")
    assert res_ok["approval_required"] is False
    assert "750" in res_ok["answer"]
    assert res_ok["status"] == "COMPLETED"


def test_day9_langgraph_conversation_memory_followup():
    """LangGraph remembers previous permission across turns in the same thread."""
    run_graph("Convert rwxr-x--- into octal", approved=True, thread_id="test_mem_thread")

    res_followup = run_graph(
        "What does this permission mean?", approved=True, thread_id="test_mem_thread"
    )
    assert "750" in res_followup["answer"] or "rwxr-x---" in res_followup["answer"]


def test_day9_langgraph_thread_isolation():
    """Separate thread IDs maintain independent conversation memories."""
    run_graph("Convert rw------- into octal", approved=True, thread_id="thread_user_A")

    res_b = run_graph("How can I find files?", thread_id="thread_user_B")
    assert "rw-------" not in res_b["answer"]


def test_day9_api_agent_approval_flow():
    """POST /agent handles initial pause and subsequent approval."""
    r1 = client.post(
        "/agent", json={"question": "Convert rwxr-x--- into octal", "thread_id": "api_user_appr"}
    )
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["approval_required"] is True
    assert d1["tool_used"] == "chmod_calculator"
    assert d1["thread_id"] == "api_user_appr"

    r2 = client.post("/agent", json={"approved": True, "thread_id": "api_user_appr"})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["approval_required"] is False
    assert "750" in d2["answer"]


def test_day9_api_agent_rejection_flow():
    """POST /agent handles rejection correctly."""
    client.post(
        "/agent", json={"question": "Convert rwxr-x--- into octal", "thread_id": "api_user_rej"}
    )
    r_rej = client.post("/agent", json={"approved": False, "thread_id": "api_user_rej"})
    assert r_rej.status_code == 200
    d_rej = r_rej.json()
    assert "rejected" in d_rej["answer"].lower()
    assert d_rej["approval_required"] is False


def test_day9_api_agent_preapproved():
    """POST /agent executes immediately when approved=True is sent upfront."""
    payload = {"question": "Convert chmod 755 to symbolic", "approved": True}
    r = client.post("/agent", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["tool_used"] == "chmod_calculator"
    assert "rwxr-xr-x" in data["answer"]


def test_day9_api_agent_invalid_input():
    """POST /agent returns 422 for empty inputs with no question or approval."""
    r = client.post("/agent", json={})
    assert r.status_code == 422


def test_day10_placeholder_detection_and_extraction():
    """Verify Day 10 dynamic placeholder detection and extraction."""
    assert has_placeholders("cp {{source}} {{destination}}") is True
    assert has_placeholders("ls -la") is False

    placeholders = extract_placeholders(
        "tar -czvf {{archive.tar.gz}} {{directory}} {{archive.tar.gz}}"
    )
    assert placeholders == ["archive.tar.gz", "directory"]


def test_day10_placeholder_template_parsing():
    """Verify extracting commands from markdown code blocks and inline snippets."""
    text = (
        "Run this command:\n"
        "```bash\n"
        "grep -rn {{pattern}} {{path/to/dir}}\n"
        "```\n"
        "Or use `chmod {{permission}} {{file}}`"
    )
    templates = find_command_templates(text)
    assert len(templates) >= 2
    assert any("grep -rn {{pattern}}" in t for t in templates)
    assert any("chmod {{permission}}" in t for t in templates)


def test_day10_placeholder_fill_logic():
    """Verify placeholder replacement logic preserving structure."""
    template = "cp {{source}} {{destination}}"
    filled = fill_template(template, {"source": "report.pdf", "destination": "/backups/"})
    assert filled == "cp report.pdf /backups/"

    partial = fill_template(template, {"source": "data.csv"})
    assert partial == "cp data.csv {{destination}}"


def test_day10_feedback_submission_and_retrieval():
    """Verify Day 10 feedback recording and retrieval API."""
    res_pos = client.post(
        "/feedback",
        json={
            "question": "How do I extract a tar.gz file?",
            "answer": "Use `tar -xzvf {{archive.tar.gz}}`",
            "rating": "helpful",
            "thread_id": "all_days_test_user",
        },
    )
    assert res_pos.status_code == 200
    assert res_pos.json()["status"] == "success"

    res_neg = client.post(
        "/feedback",
        json={
            "question": "Irrelevant query",
            "answer": "I don't know.",
            "rating": "not_helpful",
            "thread_id": "all_days_test_user",
        },
    )
    assert res_neg.status_code == 200

    res_get = client.get("/feedback")
    assert res_get.status_code == 200
    feed_data = res_get.json()
    assert feed_data["total"] >= 2
    assert feed_data["helpful"] >= 1
    assert feed_data["not_helpful"] >= 1


def test_day10_feedback_validation():
    """Verify 422 error on invalid rating values."""
    res = client.post("/feedback", json={"question": "q", "answer": "a", "rating": "invalid_val"})
    assert res.status_code == 422


def test_day10_ui_module_import():
    """Verify ui/app.py can be imported without errors."""
    import ui.app as streamlit_app

    assert hasattr(streamlit_app, "check_backend_health")
    assert hasattr(streamlit_app, "send_ask_request")
    assert hasattr(streamlit_app, "send_agent_request")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
