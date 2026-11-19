"""
smart_search.py - TF-IDF and Cosine Similarity Smart Search for ShellSathi
"""

import math
import re
from typing import Any, Dict, List

from app.records import load_records


def _tokenize(text: str) -> List[str]:
    """Extract lowercase alphanumeric tokens."""
    return re.findall(r"[a-z0-9_\-]+", text.lower())


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Compute sublinear term frequency."""
    tf = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    return {t: 1.0 + math.log(count) for t, count in tf.items()}


def search_records(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search command records using TF-IDF and Cosine Similarity.
    """
    records = load_records()
    if not query or not query.strip() or not records:
        return []

    q_tokens = _tokenize(query)
    if not q_tokens:
        return []

    # Build corpus tokens
    corpus = []
    doc_freq = {}
    for r in records:
        doc_text = f"{r.get('command', '')} {r.get('description', '')} {r.get('example_task', '')} {r.get('example_command', '')}"
        tokens = _tokenize(doc_text)
        corpus.append(tokens)
        for t in set(tokens):
            doc_freq[t] = doc_freq.get(t, 0) + 1

    num_docs = len(corpus)
    idf = {t: math.log((num_docs + 1) / (df + 1)) + 1.0 for t, df in doc_freq.items()}

    # Query vector
    q_tf = compute_tf(q_tokens)
    q_vec = {t: q_tf[t] * idf.get(t, 1.0) for t in q_tf}
    q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1.0

    scored = []
    for idx, (rec, tokens) in enumerate(zip(records, corpus)):
        d_tf = compute_tf(tokens)
        d_vec = {t: d_tf[t] * idf.get(t, 1.0) for t in d_tf}
        d_norm = math.sqrt(sum(v * v for v in d_vec.values())) or 1.0

        # Dot product
        dot = sum(q_vec[t] * d_vec.get(t, 0.0) for t in q_vec)
        score = dot / (q_norm * d_norm)

        # Keyword booster on command name
        if rec.get("command", "").lower() in q_tokens:
            score += 0.3

        if score > 0.05:
            item = rec.copy()
            item["score"] = round(float(score), 4)
            scored.append(item)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]
