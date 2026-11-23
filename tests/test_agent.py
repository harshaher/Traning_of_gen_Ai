"""
test_agent.py - Unit & Integration Tests for ShellSathi Autonomous Agent (Day 11 S1-E)

Tests:
  1. Agent selects chmod_calculator for permission queries.
  2. Agent selects RAG documentation retrieval for command lookups.
  3. Agent pauses for human-in-the-loop approval on chmod operations.
  4. Agent resumes execution when approval is granted.
  5. Agent cancels cleanly when action is rejected.
  6. Agent conversation memory persistence across turns.
"""

from app.agent_loop import run_agent_loop
from app.graph import run_graph


def test_agent_chmod_tool_selection():
    """Verify that agent detects chmod requests and triggers chmod_calculator."""
    result = run_agent_loop("Convert rwxr-x--- into octal", approved=True)
    assert result["tool_used"] == "chmod_calculator"
    assert "750" in result["answer"]


def test_agent_rag_selection():
    """Verify that agent routes documentation questions to RAG."""
    result = run_agent_loop("How do I search for files by name?", approved=True)
    assert result["tool_used"] in {"rag", "search", "rag_search"}
    assert "find" in result["answer"].lower() or "grep" in result["answer"].lower()


def test_agent_graph_approval_pause_and_resume():
    """Verify LangGraph agent approval interruption and resumption workflow."""
    thread_id = "test_agent_day11_user"

    res1 = run_graph(
        question="Convert rwxr-x--- into octal",
        thread_id=thread_id,
        approved=None,
    )
    assert res1["approval_required"] is True
    assert res1["tool_used"] == "chmod_calculator"

    res2 = run_graph(
        question="",
        thread_id=thread_id,
        approved=True,
    )
    assert res2["approval_required"] is False
    assert "750" in res2["answer"]


def test_agent_graph_approval_rejection():
    """Verify that rejecting approval safely terminates the action without execution."""
    thread_id = "test_agent_rej_user"

    run_graph(
        question="Convert 777 to symbolic",
        thread_id=thread_id,
        approved=None,
    )

    res_rej = run_graph(
        question="",
        thread_id=thread_id,
        approved=False,
    )
    assert res_rej["approval_required"] is False
    assert "rejected" in res_rej["answer"].lower() or "cancelled" in res_rej["answer"].lower()


def test_agent_memory_continuity():
    """Verify that thread memory retains previous context for follow-up questions."""
    thread_id = "test_agent_memory_flow"

    res1 = run_graph(
        question="Convert 750 to symbolic",
        thread_id=thread_id,
        approved=True,
    )
    assert "rwxr-x---" in res1["answer"]

    res2 = run_graph(
        question="What does this permission mean?",
        thread_id=thread_id,
        approved=True,
    )
    assert "750" in res2["answer"] or "rwxr-x---" in res2["answer"]
    assert "owner" in res2["answer"].lower()
