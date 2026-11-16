"""
agent_loop.py - Simple hand-written agent loop for ShellSathi (Day 9)
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import re
from typing import Any, Dict, List, Optional

from app.tools import chmod_calculator, check_destructive_command
from app.rag import answer_with_rag


def run_agent(question: str, approved: bool = False) -> Dict[str, Any]:
    """
    Hand-written autonomous agent loop:
      1. Analyzes user intent (permission calculation vs command inquiry).
      2. Executes specialized tools without unnecessary calls.
      3. Intercepts destructive actions for human approval.
      4. Returns structured results with clear explanations.
    """
    clean_q = question.strip()
    if not clean_q:
        return {
            "question": question,
            "intent": "unknown",
            "tools_used": [],
            "answer": "Please ask a question about Linux commands or permissions.",
            "approval_required": False,
            "sources": [],
        }

    tools_used: List[str] = []

    # 1. Check for destructive risk requiring approval
    safety_check = check_destructive_command(clean_q)
    if safety_check["destructive"] and not approved:
        return {
            "question": clean_q,
            "intent": "destructive_command",
            "tools_used": ["check_destructive_command"],
            "answer": (
                f"SAFETY WARNING: {safety_check['warning']}\n"
                "This action can cause irreversible system modification or data loss.\n"
                "Please confirm your approval to proceed with this command."
            ),
            "approval_required": True,
            "sources": [],
        }

    # 2. Check if the question asks for chmod / permission calculation
    q_lower = clean_q.lower()
    perm_match = re.search(r"\b([0-7]{3}|[rwx\-]{9})\b", clean_q)
    is_chmod_query = "chmod" in q_lower or "permission" in q_lower or "octal" in q_lower or "symbolic" in q_lower

    if perm_match and is_chmod_query:
        perm_str = perm_match.group(1)
        calc_result = chmod_calculator(perm_str)
        tools_used.append("chmod_calculator")

        if calc_result["valid"]:
            bd = calc_result["breakdown"]
            answer = (
                f"Permission Analysis for '{perm_str}':\n"
                f"- Octal: {calc_result['octal']}\n"
                f"- Symbolic: {calc_result['symbolic']}\n\n"
                f"Detailed Breakdown:\n"
                f"- {bd['owner']['entity']}: {bd['owner']['summary']}\n"
                f"- {bd['group']['entity']}: {bd['group']['summary']}\n"
                f"- {bd['others']['entity']}: {bd['others']['summary']}\n\n"
                f"Usage Example: chmod {calc_result['octal']} filename"
            )
            return {
                "question": clean_q,
                "intent": "chmod_conversion",
                "tools_used": tools_used,
                "answer": answer,
                "approval_required": False,
                "sources": ["https://man7.org/linux/man-pages/man1/chmod.1.html"],
            }
        else:
            return {
                "question": clean_q,
                "intent": "chmod_conversion",
                "tools_used": tools_used,
                "answer": calc_result["error"],
                "approval_required": False,
                "sources": [],
            }

    # 3. Standard Linux command inquiry -> Call RAG Tool
    tools_used.append("rag_retrieval")
    rag_result = answer_with_rag(clean_q, top_k=3)

    return {
        "question": clean_q,
        "intent": "linux_command_inquiry",
        "tools_used": tools_used,
        "answer": rag_result["answer"],
        "approval_required": False,
        "sources": rag_result["sources"],
    }


if __name__ == "__main__":
    r1 = run_agent("What is chmod 750?")
    print("Test 1 (chmod):", r1["intent"], "->", r1["tools_used"])
    print(r1["answer"])

    r2 = run_agent("rm -rf /")
    print("\nTest 2 (destructive):", r2["approval_required"], "->", r2["answer"])
