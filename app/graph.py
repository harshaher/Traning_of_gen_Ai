"""
graph.py - LangGraph Stateful Workflow for ShellSathi Agent (Day 9)
Includes input, intent detection, RAG search, chmod calculator, approval, and response nodes
with conversation memory via MemorySaver checkpointer.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
from typing import Any, Dict, List, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

from app.rag import answer_with_rag, is_out_of_scope
from app.tools import check_destructive_command, chmod_calculator


class AgentState(TypedDict, total=False):
    question: str
    thread_id: str
    intent: str
    tool_used: str
    tools_used: List[str]
    tool_output: Dict[str, Any]
    approval_required: bool
    approved: Optional[bool]
    status: str
    answer: str
    sources: List[str]
    messages: List[Dict[str, str]]
    last_permission: Optional[str]


def extract_perm_token(text: str) -> Optional[str]:
    """Helper to extract permission tokens (e.g. 755, rwxr-x---)."""
    # Check 9-character symbolic first
    m_sym = re.search(r"([rwx\-]{9})", text)
    if m_sym:
        return m_sym.group(1)
    # Check 3-digit octal
    m_oct = re.search(r"\b([0-7]{3})\b", text)
    if m_oct:
        return m_oct.group(1)
    return None


# ----------------------------------------------------
# 1. Input Node
# ----------------------------------------------------
def input_node(state: AgentState) -> Dict[str, Any]:
    """Accepts user input and maintains conversation history."""
    q = state.get("question", "").strip()
    history = state.get("messages", [])
    new_history = list(history)
    if q:
        new_history.append({"role": "user", "content": q})

    return {
        "question": q,
        "messages": new_history,
        "tools_used": state.get("tools_used", []),
    }


# ----------------------------------------------------
# 2. Intent Detection Node
# ----------------------------------------------------
def intent_node(state: AgentState) -> Dict[str, Any]:
    """Determines user intent: chmod calculation vs RAG Linux search vs destructive command."""
    q = state.get("question", "").lower()

    # Check for destructive commands first
    safety = check_destructive_command(state.get("question", ""))
    if safety["destructive"] and not state.get("approved"):
        return {
            "intent": "destructive",
            "tool_output": safety,
            "approval_required": True,
        }

    # Check for chmod / permission requests
    perm_keywords = ["chmod", "permission", "octal", "symbolic", "convert", "mean", "rwx"]
    has_perm_keyword = any(kw in q for kw in perm_keywords)
    has_perm_token = bool(extract_perm_token(state.get("question", "")))
    has_memory_perm = bool(state.get("last_permission"))

    if has_perm_token or (has_perm_keyword and (has_memory_perm or "permission" in q)):
        return {"intent": "chmod"}

    return {"intent": "rag"}


# ----------------------------------------------------
# 3. chmod Calculator Tool Node
# ----------------------------------------------------
def chmod_node(state: AgentState) -> Dict[str, Any]:
    """Executes the chmod calculator tool, using query token or conversation memory."""
    q = state.get("question", "")
    token = extract_perm_token(q)
    # If no token in current question, use previous permission from thread memory
    target_perm = token if token else state.get("last_permission", "750")

    calc = chmod_calculator(target_perm)
    tools = list(state.get("tools_used", []))
    if "chmod_calculator" not in tools:
        tools.append("chmod_calculator")

    return {
        "tool_used": "chmod_calculator",
        "tools_used": tools,
        "tool_output": calc,
        "last_permission": calc.get("converted_permission", target_perm) if calc.get("valid") else state.get("last_permission"),
    }


# ----------------------------------------------------
# 4. RAG Search Tool Node
# ----------------------------------------------------
def rag_node(state: AgentState) -> Dict[str, Any]:
    """Executes RAG retrieval over ShellSathi Linux manual collection."""
    q = state.get("question", "")
    tools = list(state.get("tools_used", []))
    if "rag_search" not in tools:
        tools.append("rag_search")

    # Honest refusal for out of scope questions
    if is_out_of_scope(q):
        output = {
            "answer": "I don't know based on the available ShellSathi knowledge. This question is outside Linux command documentation.",
            "sources": [],
            "confidence": 0.0,
        }
    else:
        output = answer_with_rag(q, top_k=3)

    return {
        "tool_used": "rag_search",
        "tools_used": tools,
        "tool_output": output,
    }


# ----------------------------------------------------
# 5. Approval Node
# ----------------------------------------------------
def approval_node(state: AgentState) -> Dict[str, Any]:
    """
    Approval step: pauses for human approval on chmod permission operations
    and destructive commands, or resumes when confirmed/rejected.
    """
    intent = state.get("intent", "rag")

    # Destructive commands require approval
    if intent == "destructive":
        if state.get("approved") is True:
            return {"status": "APPROVED", "approval_required": False}
        elif state.get("approved") is False:
            return {"status": "REJECTED", "approval_required": False}
        else:
            decision = interrupt({
                "action": "destructive_command_approval",
                "warning": state.get("tool_output", {}).get("warning", "Destructive command"),
            })
            return {
                "approved": bool(decision),
                "approval_required": False,
                "status": "APPROVED" if decision else "REJECTED",
            }

    # chmod operations require approval
    if intent == "chmod":
        # If approval state is not yet provided, interrupt for approval
        if state.get("approved") is None:
            calc = state.get("tool_output", {})
            decision = interrupt({
                "action": "chmod_approval",
                "input_permission": calc.get("input_permission", ""),
                "converted_permission": calc.get("converted_permission", ""),
            })
            return {
                "approved": bool(decision),
                "approval_required": False,
                "status": "APPROVED" if decision else "REJECTED",
            }
        elif state.get("approved") is True:
            return {"status": "APPROVED", "approval_required": False}
        else:
            return {"status": "REJECTED", "approval_required": False}

    # Safe RAG queries do not require approval
    return {"status": "APPROVED", "approval_required": False}


# ----------------------------------------------------
# 6. Response Node
# ----------------------------------------------------
def response_node(state: AgentState) -> Dict[str, Any]:
    """Constructs the final response and updates conversation history."""
    status = state.get("status", "COMPLETED")
    intent = state.get("intent", "rag")

    if status == "REJECTED":
        final_answer = "Operation was rejected by the user. The chmod permission calculation/application was cancelled."
        sources = []
    elif intent == "chmod":
        calc = state.get("tool_output", {})
        if calc.get("valid"):
            final_answer = (
                f"The octal permission is {calc.get('octal')} "
                f"(Symbolic: {calc.get('symbolic')}).\n"
                f"- Owner: {calc.get('owner_permissions')}\n"
                f"- Group: {calc.get('group_permissions')}\n"
                f"- Others: {calc.get('others_permissions')}\n\n"
                f"{calc.get('explanation')}"
            )
            sources = ["https://man7.org/linux/man-pages/man1/chmod.1.html"]
        else:
            final_answer = calc.get("error", "Invalid permission.")
            sources = []
    elif intent == "destructive":
        final_answer = (
            f"Approved destructive operation: {state.get('question')}\n"
            "Warning: Please execute carefully in your terminal."
        )
        sources = []
    else:
        # RAG output
        rag_out = state.get("tool_output", {})
        final_answer = rag_out.get("answer", "No answer found.")
        sources = rag_out.get("sources", [])

    history = list(state.get("messages", []))
    history.append({"role": "assistant", "content": final_answer})

    return {
        "final_answer": final_answer,
        "answer": final_answer,
        "sources": sources,
        "messages": history,
        "status": "COMPLETED" if status != "REJECTED" else "REJECTED",
        "approval_required": False,
    }


# ----------------------------------------------------
# Routing Logic
# ----------------------------------------------------
def route_intent(state: AgentState) -> str:
    """Conditional routing edge."""
    intent = state.get("intent", "rag")
    if intent == "chmod":
        return "chmod_node"
    return "rag_node"


# ----------------------------------------------------
# Build the 6-Node LangGraph StateGraph
# ----------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("input_node", input_node)
workflow.add_node("intent_node", intent_node)
workflow.add_node("chmod_node", chmod_node)
workflow.add_node("rag_node", rag_node)
workflow.add_node("approval_node", approval_node)
workflow.add_node("response_node", response_node)

workflow.add_edge(START, "input_node")
workflow.add_edge("input_node", "intent_node")
workflow.add_conditional_edges(
    "intent_node",
    route_intent,
    {
        "chmod_node": "chmod_node",
        "rag_node": "rag_node",
    },
)
workflow.add_edge("chmod_node", "approval_node")
workflow.add_edge("rag_node", "approval_node")
workflow.add_edge("approval_node", "response_node")
workflow.add_edge("response_node", END)

# In-memory checkpointer for conversation memory
agent_memory = MemorySaver()
agent_graph = workflow.compile(checkpointer=agent_memory)


# ----------------------------------------------------
# Execution Helper Function
# ----------------------------------------------------
def run_graph(
    question: str,
    approved: Optional[bool] = None,
    thread_id: str = "default_user",
) -> Dict[str, Any]:
    """
    Executes or resumes the LangGraph workflow:
      - Automatically detects interrupted state for thread_id and resumes with approval/rejection.
      - Maintains conversation history across multiple messages in the same thread.
      - Isolates memory between distinct thread_ids.
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Check if this thread has an active interrupt awaiting approval
    state_snap = agent_graph.get_state(config)
    if state_snap.tasks and any(t.interrupts for t in state_snap.tasks):
        # Resume the interrupted execution
        decision = approved if approved is not None else (question.lower().strip() in ["yes", "y", "approve", "confirm"])
        out = agent_graph.invoke(Command(resume=decision), config=config)
        return {
            "question": question,
            "thread_id": thread_id,
            "intent": out.get("intent", "general"),
            "tool_used": out.get("tool_used", "none"),
            "tools_used": out.get("tools_used", []),
            "answer": out.get("answer", out.get("final_answer", "")),
            "approval_required": False,
            "approved": decision,
            "status": out.get("status", "COMPLETED"),
            "sources": out.get("sources", []),
        }

    # Fresh turn
    input_data: AgentState = {
        "question": question,
        "thread_id": thread_id,
        "approved": approved,
    }

    out = agent_graph.invoke(input_data, config=config)

    # Check if execution paused at an interrupt for approval
    if out.get("__interrupt__"):
        inter_val = out["__interrupt__"][0].value if out["__interrupt__"] else {}
        action = inter_val.get("action", "operation")
        input_perm = inter_val.get("input_permission", "")
        converted_perm = inter_val.get("converted_permission", "")

        answer_msg = (
            f"Approval required for {action}: "
            f"Convert '{input_perm}' to '{converted_perm}'. "
            "Please confirm (approved=true to proceed, or approved=false to cancel)."
        )
        return {
            "question": question,
            "thread_id": thread_id,
            "intent": "chmod" if "chmod" in action else "destructive",
            "tool_used": "chmod_calculator" if "chmod" in action else "safety_check",
            "tools_used": ["chmod_calculator"] if "chmod" in action else ["safety_check"],
            "answer": answer_msg,
            "approval_required": True,
            "approved": None,
            "status": "PENDING_APPROVAL",
            "sources": [],
        }

    return {
        "question": question,
        "thread_id": thread_id,
        "intent": out.get("intent", "general"),
        "tool_used": out.get("tool_used", "none"),
        "tools_used": out.get("tools_used", []),
        "answer": out.get("answer", out.get("final_answer", "")),
        "approval_required": out.get("approval_required", False),
        "approved": out.get("approved"),
        "status": out.get("status", "COMPLETED"),
        "sources": out.get("sources", []),
    }


# Backwards-compatible alias
run_shellsathi_graph = run_graph


if __name__ == "__main__":
    print("--- Test 1: Start chmod conversion (interrupted for approval) ---")
    r1 = run_graph("Convert rwxr-x--- into octal", thread_id="demo_user")
    print(r1)

    print("\n--- Test 2: Approve the pending chmod conversion ---")
    r2 = run_graph("", approved=True, thread_id="demo_user")
    print(r2)

    print("\n--- Test 3: Follow-up question using conversation memory ---")
    r3 = run_graph("What does this permission mean?", approved=True, thread_id="demo_user")
    print(r3)

    print("\n--- Test 4: Safe RAG Search (no approval needed) ---")
    r4 = run_graph("How can I find a file named test.txt in Linux?", thread_id="demo_user_2")
    print(r4)
