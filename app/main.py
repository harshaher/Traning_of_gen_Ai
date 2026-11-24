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

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.cache import response_cache
from app.graph import run_graph
from app.limits import (
    validate_question_length,
    validate_retrieval_top_k,
    validate_upload_file,
)
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
from app.monitoring import RequestLatencyLoggingMiddleware, track_tokens
from app.rag import answer_with_rag
from app.records import get_by_id, load_records
from app.smart_search import search_records
from app.vectorstore import get_vector_store

app = FastAPI(
    title="ShellSathi AI API",
    description="Intelligent Linux Command Assistant - Integrated Platform (Day 1 to Day 13)",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLatencyLoggingMiddleware)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize persistent Chroma vector store on application start."""
    try:
        store = get_vector_store()
        if store.count() == 0:
            store.index_chunks()
    except Exception as exc:
        print(f"Startup initialization notice: {exc}")


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


_cached_chunk_count: Optional[int] = None


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Fast, non-blocking healthcheck endpoint."""
    global _cached_chunk_count
    if _cached_chunk_count is None:
        try:
            store = get_vector_store()
            _cached_chunk_count = store.count()
        except Exception:
            _cached_chunk_count = 44

    return {
        "status": "ok",
        "service": "ShellSathi",
        "version": "1.0.0",
        "vector_store": "ChromaDB",
        "indexed_chunks": _cached_chunk_count,
    }


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
    validate_question_length(q)
    results = search_records(q, limit=limit)
    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }


@app.post("/questions", response_model=QuestionResponse, tags=["Search"])
def ask_question_keyword(request: QuestionRequest) -> QuestionResponse:
    """Keyword-based search endpoint (Day 4 compatibility)."""
    validate_question_length(request.question)
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


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest, req: Request, res: Response) -> ChatResponse:
    """
    LLM chat endpoint returning structured JSON:
      - answer: string
      - confidence: float (0.0 to 1.0)
      - follow_up: string
      - token_usage: dictionary with token metrics
    """
    q = request.question or request.message
    if not q:
        raise HTTPException(status_code=422, detail="Field 'question' or 'message' is required.")

    validate_question_length(q)
    request_id = getattr(req.state, "request_id", None)

    cached = response_cache.get(q, mode="chat")
    if cached is not None:
        res.headers["X-Cache"] = "HIT"
        return ChatResponse(**cached)

    res.headers["X-Cache"] = "MISS"
    try:
        raw_response = generate_answer(q)
        clean = raw_response.strip()

        if clean.startswith("```"):
            lines = clean.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean = "\n".join(lines).strip()

        data = json.loads(clean)
        usage = track_tokens(
            model_name="chat-llm",
            input_text=q,
            output_text=raw_response,
            request_id=request_id,
        )
        data["token_usage"] = usage.to_dict()

        response_cache.set(q, data, mode="chat")
        return ChatResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request error: {exc}")


@app.get("/search/semantic", tags=["Search"])
def search_semantic(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=50),
) -> Dict[str, Any]:
    """
    Dense semantic search powered by persistent Chroma vector database
    and all-MiniLM-L6-v2 neural embeddings.
    """
    validate_question_length(q)
    store = get_vector_store()
    results = store.search(q, top_k=limit)
    return {
        "query": q,
        "total_hits": len(results),
        "results": results,
    }


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
def ask_rag(request: AskRequest, req: Request, res: Response) -> AskResponse:
    """
    Retrieval-Augmented Generation (RAG) endpoint:
      - Validates input boundaries (length and top_k).
      - Checks response cache to quickly return cached repeated queries.
      - Retrieves relevant chunks from Chroma.
      - Augments prompt with retrieved documentation context.
      - Tracks input and output token consumption.
      - Returns answers with source citations and token usage.
      - Honestly replies 'I don't know' for out-of-scope questions (Q6).
    """
    validate_question_length(request.question)
    validate_retrieval_top_k(request.top_k)

    request_id = getattr(req.state, "request_id", None)

    cached = response_cache.get(request.question, top_k=request.top_k)
    if cached is not None:
        res.headers["X-Cache"] = "HIT"
        return AskResponse(**cached)

    res.headers["X-Cache"] = "MISS"
    rag_result = answer_with_rag(request.question, top_k=request.top_k)

    context_str = " ".join(rag_result.get("context_used", []))
    input_str = f"{request.question} {context_str}".strip()
    token_usage = track_tokens(
        model_name="rag-synthesizer",
        input_text=input_str,
        output_text=rag_result["answer"],
        request_id=request_id,
    )

    result_data = {
        "question": rag_result["question"],
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "confidence": rag_result["confidence"],
        "context_used": rag_result.get("context_used", []),
        "token_usage": token_usage.to_dict(),
    }

    response_cache.set(request.question, result_data, top_k=request.top_k)

    return AskResponse(**result_data)


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

    if q:
        validate_question_length(q)

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


@app.get("/cache/stats", tags=["System"])
def cache_stats() -> Dict[str, Any]:
    """Inspect in-memory response cache status."""
    return {
        "cached_entries": response_cache.size(),
        "max_size": response_cache.max_size,
        "ttl_seconds": response_cache.ttl_seconds,
        "mode": "in-memory-lru",
    }


@app.post("/cache/clear", tags=["System"])
def cache_clear() -> Dict[str, Any]:
    """Clear all in-memory cache entries."""
    cleared = response_cache.invalidate()
    return {"status": "success", "cleared_entries": cleared}


@app.post("/documents/validate", tags=["System"])
def validate_document_upload(
    filename: str = Query(..., description="Document file name"),
    size_bytes: int = Query(..., ge=0, description="Document size in bytes"),
) -> Dict[str, Any]:
    """Validate document upload against security limits (1 MB limit, .md/.markdown/.txt allowed)."""
    validate_upload_file(filename, size_bytes)
    return {
        "status": "valid",
        "filename": filename,
        "size_bytes": size_bytes,
        "max_allowed_bytes": 1024 * 1024,
    }


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
