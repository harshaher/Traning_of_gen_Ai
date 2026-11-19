"""
main.py - ShellSathi Unified FastAPI Application (Days 1 to 9)

Integrates:
  - Day 4: Records, Smart Search (/health, /records, /search, /questions)
  - Day 6: LLM Chat (/chat)
  - Day 7: Vector Semantic Search (/search/semantic)
  - Day 8: Complete RAG System (/ask)
  - Day 9: Autonomous Agent (/agent) with chmod tools and approval workflow
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query

from app.graph import run_graph
from app.llm import generate_answer
from app.models import (
    AgentRequest,
    AgentResponse,
    AskRequest,
    AskResponse,
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    QuestionRequest,
    QuestionResponse,
)
from app.rag import answer_with_rag
from app.records import get_by_id, load_records
from app.smart_search import search_records
from app.vectorstore import get_vector_store

app = FastAPI(
    title="ShellSathi AI API",
    description="Intelligent Linux Command Assistant - Integrated Platform (Day 1 to Day 9)",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize persistent Chroma vector store on application start."""
    try:
        store = get_vector_store()
        if store.count() == 0:
            store.index_chunks()
    except Exception as exc:
        print(f"Startup initialization notice: {exc}")


# --- System Endpoints ---

@app.get("/", tags=["System"])
def root() -> Dict[str, Any]:
    """Root status and API feature inventory."""
    return {
        "service": "ShellSathi Linux AI Assistant",
        "version": "1.0.0",
        "description": "Unified platform integrating Day 1 to Day 9 capabilities",
        "features": [
            "Day 2/4: Command records & TF-IDF smart search (/records, /search)",
            "Day 6: LLM chat with strict JSON schema (/chat)",
            "Day 7: Neural semantic search via ChromaDB (/search/semantic)",
            "Day 8: Full RAG retrieval with source citations (/ask)",
            "Day 9: LangGraph agent with chmod calculator & safety approvals (/agent)",
        ],
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Healthcheck endpoint."""
    store = get_vector_store()
    return {
        "status": "ok",
        "service": "ShellSathi",
        "version": "1.0.0",
        "vector_store": "ChromaDB",
        "indexed_chunks": store.count(),
    }


# --- Day 2 & Day 4: Records and Smart Search ---

@app.get("/records", tags=["Records"])
def get_records(
    limit: int = Query(default=10, ge=1, le=100),
    command: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """Retrieve Linux command records."""
    records = load_records()
    if command:
        records = [r for r in records if r.get("command", "").lower() == command.lower()]

    showing = records[:limit]
    return {
        "total": len(records),
        "showing": len(showing),
        "records": showing,
    }


@app.get("/records/{record_id}", tags=["Records"])
def get_single_record(record_id: str) -> Dict[str, Any]:
    """Retrieve record by ID or command name. Returns 404 if not found."""
    records = load_records()
    rec = get_by_id(records, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail=f"Record '{record_id}' not found.")
    return rec


@app.get("/search", tags=["Search"])
def search_tfidf(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=50),
) -> Dict[str, Any]:
    """Search records using TF-IDF and cosine similarity."""
    results = search_records(q, limit=limit)
    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }


@app.post("/questions", response_model=QuestionResponse, tags=["Search"])
def ask_question_keyword(request: QuestionRequest) -> QuestionResponse:
    """Keyword-based search endpoint (Day 4 compatibility)."""
    results = search_records(request.question, limit=5)
    answer = (
        "Here are the relevant Linux commands matching your query."
        if results
        else "No matching Linux command found."
    )
    return QuestionResponse(
        question=request.question,
        total_results=len(results),
        answer=answer,
        results=results,
    )


# --- Day 6: LLM Integration ---

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest) -> ChatResponse:
    """
    LLM chat endpoint returning structured JSON:
      - answer: string
      - confidence: float (0.0 to 1.0)
      - follow_up: string
    """
    q = request.question or request.message
    if not q:
        raise HTTPException(status_code=422, detail="Field 'question' or 'message' is required.")
    try:
        raw_response = generate_answer(q)
        clean = raw_response.strip()

        # Strip code fences if present
        if clean.startswith("```"):
            lines = clean.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean = "\n".join(lines).strip()

        data = json.loads(clean)
        return ChatResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request error: {exc}")


# --- Day 7: Vector Semantic Search ---

@app.get("/search/semantic", tags=["Search"])
def search_semantic(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=50),
) -> Dict[str, Any]:
    """
    Dense semantic search powered by persistent Chroma vector database
    and all-MiniLM-L6-v2 neural embeddings.
    """
    store = get_vector_store()
    results = store.search(q, top_k=limit)
    return {
        "query": q,
        "total_hits": len(results),
        "results": results,
    }


# --- Day 8: Complete RAG System ---

@app.post("/ask", response_model=AskResponse, tags=["RAG"])
def ask_rag(request: AskRequest) -> AskResponse:
    """
    Retrieval-Augmented Generation (RAG) endpoint:
      - Retrieves relevant chunks from Chroma.
      - Augments prompt with retrieved documentation context.
      - Returns answers with source citations.
      - Honestly replies 'I don't know' for out-of-scope questions (Q6).
    """
    rag_result = answer_with_rag(request.question, top_k=request.top_k)
    return AskResponse(
        question=rag_result["question"],
        answer=rag_result["answer"],
        sources=rag_result["sources"],
        confidence=rag_result["confidence"],
        context_used=rag_result.get("context_used", []),
    )


# --- Day 9: Autonomous Agent with Tools & Approvals ---

@app.post("/agent", response_model=AgentResponse, tags=["Agent"])
def agent_endpoint(request: AgentRequest) -> AgentResponse:
    """
    LangGraph Autonomous Agent endpoint:
      - Classifies intent (chmod tool, RAG inquiry, destructive command).
      - Executes specialized tools without unnecessary calls.
      - Maintains thread-specific conversation memory.
      - Enforces approval step for permission conversions and destructive operations.
      - Resumes interrupted workflow on approval/rejection.
    """
    q = (request.question or "").strip()
    if not q and request.approved is None:
        raise HTTPException(
            status_code=422,
            detail="Either 'question' or an approval decision ('approved') must be provided.",
        )

    try:
        agent_output = run_graph(
            question=q,
            approved=request.approved,
            thread_id=request.thread_id or "default_user",
        )
        return AgentResponse(
            answer=agent_output["answer"],
            tool_used=agent_output.get("tool_used", "none"),
            approval_required=agent_output.get("approval_required", False),
            thread_id=agent_output.get("thread_id", request.thread_id or "default_user"),
            question=agent_output.get("question", q),
            intent=agent_output.get("intent", "general"),
            tools_used=agent_output.get("tools_used", []),
            status=agent_output.get("status", "COMPLETED"),
            sources=agent_output.get("sources", []),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(exc)}")


# --- Day 10: Feedback Persistence Endpoints ---

FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.json"


def _read_feedback_storage() -> List[Dict[str, Any]]:
    """Helper to safely read feedback entries from data/feedback.json."""
    if not FEEDBACK_FILE.exists():
        return []
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except Exception:
        return []


def _write_feedback_storage(entries: List[Dict[str, Any]]) -> None:
    """Helper to safely write feedback entries to data/feedback.json."""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
def submit_feedback(feedback: FeedbackRequest) -> FeedbackResponse:
    """
    Save user feedback (Helpful / Not Helpful) with timestamp and thread context.
    Persists data to data/feedback.json.
    """
    rating_clean = feedback.rating.strip().lower()
    if rating_clean not in {"helpful", "not_helpful", "thumbs_up", "thumbs_down"}:
        raise HTTPException(
            status_code=422,
            detail="Rating must be 'helpful' or 'not_helpful'.",
        )

    # Normalize rating to helpful / not_helpful
    normalized_rating = "helpful" if rating_clean in {"helpful", "thumbs_up"} else "not_helpful"
    timestamp = feedback.timestamp or datetime.now(timezone.utc).isoformat()

    entry = {
        "question": feedback.question,
        "answer": feedback.answer,
        "rating": normalized_rating,
        "timestamp": timestamp,
        "thread_id": feedback.thread_id,
    }

    entries = _read_feedback_storage()
    entries.append(entry)
    _write_feedback_storage(entries)

    return FeedbackResponse(
        status="success",
        message="Feedback recorded successfully.",
        total_feedback=len(entries),
    )


@app.get("/feedback", tags=["Feedback"])
def get_feedback() -> Dict[str, Any]:
    """Retrieve all recorded feedback entries and summary statistics."""
    entries = _read_feedback_storage()
    helpful_count = sum(1 for e in entries if e.get("rating") == "helpful")
    not_helpful_count = sum(1 for e in entries if e.get("rating") == "not_helpful")

    return {
        "total": len(entries),
        "helpful": helpful_count,
        "not_helpful": not_helpful_count,
        "feedback": entries,
    }

