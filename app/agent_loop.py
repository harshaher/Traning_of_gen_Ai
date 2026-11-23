"""
agent_loop.py - Simple hand-written agent loop for ShellSathi (Day 9)
Implements tool selection and routing between RAG search and chmod_calculator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
from typing import Any, Dict, Optional

from app.rag import answer_with_rag, is_out_of_scope
from app.tools import check_destructive_command, chmod_calculator


def extract_permission(text: str) -> Optional[str]:
    """Extract a 3-digit octal or 9-character symbolic permission token from query."""
    m_sym = re.search(r"([rwx\-]{9})", text)
    if m_sym:
        return m_sym.group(1)
    m_oct = re.search(r"\b([0-7]{3})\b", text)
    if m_oct:
        return m_oct.group(1)
    return None


def run_agent_loop(question: str, approved: bool = False) -> Dict[str, Any]:
    """
    Hand-written autonomous agent loop:
      1. Accepts user query.
      2. Detects intent: permission calculation vs Linux command reference.
      3. Selects the appropriate tool (chmod_calculator or RAG search).
      4. Executes tool safely with error handling.
      5. Returns structured and clear response with sources/explanations.
    """
    clean_q = question.strip() if question else ""
    if not clean_q:
        return {
            "question": question,
            "intent": "unknown",
            "tool_used": "none",
            "tools_used": [],
            "answer": "Please provide a question about Linux commands or file permissions.",
            "approval_required": False,
            "sources": [],
        }

    safety = check_destructive_command(clean_q)
    if safety["destructive"] and not approved:
        return {
            "question": clean_q,
            "intent": "destructive_command",
            "tool_used": "safety_check",
            "tools_used": ["safety_check", "check_destructive_command"],
            "answer": (
                f"SAFETY WARNING: {safety['warning']}\n"
                "This action can modify or delete critical system data.\n"
                "Please provide explicit confirmation (approved=True) to proceed."
            ),
            "approval_required": True,
            "sources": [],
        }

    q_lower = clean_q.lower()

    perm_keywords = ["chmod", "permission", "octal", "symbolic", "rwx", "convert"]
    has_perm_keyword = any(kw in q_lower for kw in perm_keywords)
    perm_token = extract_permission(clean_q)

    if perm_token or (has_perm_keyword and any(ch in clean_q for ch in "01234567rwx-")):
        target = perm_token if perm_token else clean_q.strip()
        calc = chmod_calculator(target)
        tool_name = "chmod_calculator"

        if calc["valid"]:
            explanation = calc["explanation"]
            answer = (
                f"Permission Calculation Result:\n"
                f"- Input: {calc['input_permission']}\n"
                f"- Converted: {calc['converted_permission']}\n"
                f"- Owner: {calc['owner_permissions']}\n"
                f"- Group: {calc['group_permissions']}\n"
                f"- Others: {calc['others_permissions']}\n\n"
                f"{explanation}"
            )
            return {
                "question": clean_q,
                "intent": "chmod_calculation",
                "tool_used": tool_name,
                "tools_used": [tool_name],
                "answer": answer,
                "approval_required": False,
                "sources": ["https://man7.org/linux/man-pages/man1/chmod.1.html"],
            }
        elif has_perm_keyword:
            return {
                "question": clean_q,
                "intent": "chmod_calculation",
                "tool_used": tool_name,
                "tools_used": [tool_name],
                "answer": calc.get(
                    "error",
                    "Please provide a valid 3-digit octal or 9-character symbolic permission.",
                ),
                "approval_required": False,
                "sources": [],
            }

    tool_name = "rag_search"

    if is_out_of_scope(clean_q):
        return {
            "question": clean_q,
            "intent": "rag_search",
            "tool_used": tool_name,
            "tools_used": [tool_name, "rag_retrieval"],
            "answer": "I don't know based on the available ShellSathi knowledge. This question is outside Linux command documentation.",
            "approval_required": False,
            "sources": [],
        }

    rag_result = answer_with_rag(clean_q, top_k=3)

    return {
        "question": clean_q,
        "intent": "rag_search",
        "tool_used": tool_name,
        "tools_used": [tool_name, "rag_retrieval"],
        "answer": rag_result["answer"],
        "approval_required": False,
        "sources": rag_result.get("sources", []),
    }


run_agent = run_agent_loop


if __name__ == "__main__":
    print("--- Test 1: RAG Search ---")
    print(run_agent_loop("How can I find a file named test.txt in Linux?")["answer"])

    print("\n--- Test 2: Symbolic to Octal ---")
    print(run_agent_loop("Convert rwxr-x--- into octal.")["answer"])

    print("\n--- Test 3: Octal to Symbolic ---")
    print(run_agent_loop("What does chmod 755 mean?")["answer"])

    print("\n--- Test 4: Unknown Question ---")
    print(run_agent_loop("Why is our company VPN slow from the Hinjewadi office today?")["answer"])
