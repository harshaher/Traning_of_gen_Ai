"""
graph.py - LangGraph Stateful Workflow for ShellSathi Agent (Day 9)
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from app.tools import chmod_calculator, check_destructive_command
from app.rag import answer_with_rag


class AgentState(TypedDict):
    question: str
    intent: str
    tools_used: List[str]
    tool_output: Dict[str, Any]
    approval_required: bool
    approved: bool
    final_answer: str
    sources: List[str]


def classify_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Inspect user query and determine routing intent."""
    question = state["question"].lower()

    # Check destructive command risk first
    safety = check_destructive_command(state["question"])
    if safety["destructive"] and not state.get("approved", False):
        return {
            "intent": "approval",
            "approval_required": True,
            "tool_output": safety,
        }

    # Check for chmod / permission calculation
    if any(k in question for k in ["chmod", "permission", "octal", "symbolic"]):
        import re
        if re.search(r"\b([0-7]{3}|[rwx\-]{9})\b", state["question"]):
            return {"intent": "chmod", "approval_required": False}

    return {"intent": "rag", "approval_required": False}


def approval_node(state: AgentState) -> Dict[str, Any]:
    """Node 2: Intercept destructive operations and demand approval."""
    safety = state.get("tool_output", {})
    warning = safety.get("warning", "This command can cause data loss.")
    answer = (
        f"HUMAN APPROVAL REQUIRED:\n{warning}\n"
        "Please provide confirmation ('approved=True') to execute this action."
    )
    return {
        "final_answer": answer,
        "tools_used": state.get("tools_used", []) + ["safety_check"],
        "approval_required": True,
        "sources": [],
    }


def chmod_node(state: AgentState) -> Dict[str, Any]:
    """Node 3: Execute chmod calculator tool."""
    import re
    m = re.search(r"\b([0-7]{3}|[rwx\-]{9})\b", state["question"])
    perm_input = m.group(1) if m else "755"

    result = chmod_calculator(perm_input)
    tools = state.get("tools_used", []) + ["chmod_calculator"]

    if result["valid"]:
        bd = result["breakdown"]
        answer = (
            f"Permission Calculation for '{perm_input}':\n"
            f"- Octal: {result['octal']}\n"
            f"- Symbolic: {result['symbolic']}\n\n"
            f"Details:\n"
            f"- {bd['owner']['entity']}: {bd['owner']['summary']}\n"
            f"- {bd['group']['entity']}: {bd['group']['summary']}\n"
            f"- {bd['others']['entity']}: {bd['others']['summary']}"
        )
        sources = ["https://man7.org/linux/man-pages/man1/chmod.1.html"]
    else:
        answer = result["error"]
        sources = []

    return {
        "final_answer": answer,
        "tools_used": tools,
        "sources": sources,
        "approval_required": False,
    }


def rag_node(state: AgentState) -> Dict[str, Any]:
    """Node 4: Execute RAG retrieval and answer generation."""
    rag_res = answer_with_rag(state["question"], top_k=3)
    tools = state.get("tools_used", []) + ["rag_retrieval"]

    return {
        "final_answer": rag_res["answer"],
        "tools_used": tools,
        "sources": rag_res["sources"],
        "approval_required": False,
    }


def route_intent(state: AgentState) -> str:
    """Conditional routing edge."""
    intent = state.get("intent", "rag")
    if intent == "approval":
        return "approval_node"
    elif intent == "chmod":
        return "chmod_node"
    return "rag_node"


# Build the LangGraph Workflow
workflow = StateGraph(AgentState)

workflow.add_node("classify", classify_node)
workflow.add_node("approval_node", approval_node)
workflow.add_node("chmod_node", chmod_node)
workflow.add_node("rag_node", rag_node)

workflow.set_entry_point("classify")

workflow.add_conditional_edges(
    "classify",
    route_intent,
    {
        "approval_node": "approval_node",
        "chmod_node": "chmod_node",
        "rag_node": "rag_node",
    },
)

workflow.add_edge("approval_node", END)
workflow.add_edge("chmod_node", END)
workflow.add_edge("rag_node", END)

# Compile executable graph
agent_graph = workflow.compile()


def run_graph(question: str, approved: bool = False) -> Dict[str, Any]:
    """Execute the compiled LangGraph workflow."""
    initial_state: AgentState = {
        "question": question,
        "intent": "",
        "tools_used": [],
        "tool_output": {},
        "approval_required": False,
        "approved": approved,
        "final_answer": "",
        "sources": [],
    }

    final_state = agent_graph.invoke(initial_state)

    return {
        "question": final_state["question"],
        "intent": final_state.get("intent", "general"),
        "tools_used": final_state.get("tools_used", []),
        "answer": final_state.get("final_answer", ""),
        "approval_required": final_state.get("approval_required", False),
        "sources": final_state.get("sources", []),
    }


if __name__ == "__main__":
    out = run_graph("Convert chmod 644 to symbolic")
    print("Graph Output:\n", out["answer"])
    print("Tools used:", out["tools_used"])
