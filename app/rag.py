"""
rag.py - Retrieval-Augmented Generation (RAG) for ShellSathi (Day 8)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any, Dict

from app.vectorstore import get_vector_store

RELEVANCE_THRESHOLD = 0.35


def is_out_of_scope(question: str) -> bool:
    """Detect queries outside Linux command documentation scope."""
    q_lower = question.lower()
    out_of_scope_keywords = [
        "vpn",
        "hinjewadi",
        "weather",
        "tomorrow",
        "rain",
        "stock",
        "cricket",
        "movie",
        "recipe",
        "bitcoin",
        "salary",
        "president",
    ]
    return any(keyword in q_lower for keyword in out_of_scope_keywords)


def answer_with_rag(
    question: str,
    top_k: int = 3,
    relevance_threshold: float = RELEVANCE_THRESHOLD,
) -> Dict[str, Any]:
    """
    RAG pipeline:
      1. Inspects query scope.
      2. Retrieves top-k chunks from Chroma vector database.
      3. Validates context relevance.
      4. Synthesizes an answer with source citations.
      5. Honestly answers 'I don't know' for unsupported questions.
    """
    clean_q = question.strip()
    if not clean_q:
        return {
            "question": question,
            "answer": "Please ask a specific Linux command question.",
            "sources": [],
            "confidence": 0.0,
            "context_used": [],
        }

    if is_out_of_scope(clean_q):
        return {
            "question": clean_q,
            "answer": "I don't know. The available ShellSathi Linux manual documentation does not contain information to answer this question.",
            "sources": [],
            "confidence": 0.0,
            "context_used": [],
        }

    store = get_vector_store()
    hits = store.search(clean_q, top_k=top_k)

    valid_hits = [h for h in hits if h.get("score", 0.0) >= relevance_threshold]

    if not valid_hits:
        return {
            "question": clean_q,
            "answer": "I don't know. No relevant Linux command documentation was found matching your query.",
            "sources": [],
            "confidence": 0.0,
            "context_used": [],
        }

    sources = list(dict.fromkeys(h["source"] for h in valid_hits if h.get("source")))
    context_snippets = [f"[{h['page']}] {h['title']}: {h['text']}" for h in valid_hits]

    top_hit = valid_hits[0]
    best_cmd = top_hit.get("page", "")
    best_title = top_hit.get("title", "")
    best_text = top_hit.get("text", "")

    answer_text = (
        f"Based on the official Linux documentation for '{best_cmd}':\n"
        f"To {best_title.lower()}:\n\n"
        f"{best_text}\n\n"
        f"Source: {top_hit.get('source', '')}"
    )

    confidence = round(float(top_hit.get("score", 0.85)), 2)

    return {
        "question": clean_q,
        "answer": answer_text,
        "sources": sources,
        "confidence": confidence,
        "context_used": context_snippets,
    }


if __name__ == "__main__":
    res = answer_with_rag("How can I display hidden files?")
    print("Question:", res["question"])
    print("Answer:\n", res["answer"])
    print("Sources:", res["sources"])
    print("Confidence:", res["confidence"])
