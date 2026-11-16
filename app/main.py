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
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query

from app.models import (
    QuestionRequest, QuestionResponse,
    ChatRequest, ChatResponse,
    AskRequest, AskResponse,
    AgentRequest, AgentResponse
)
from app.records import load_records, get_by_id
from app.smart_search import search_records
from app.llm import generate_answer
from app.vectorstore import get_vector_store
from app.rag import answer_with_rag
from app.graph import run_graph

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
      - Enforces approval step before destructive operations.
    """
    agent_output = run_graph(request.question, approved=bool(request.approved))
    return AgentResponse(
        question=agent_output["question"],
        intent=agent_output["intent"],
        tools_used=agent_output["tools_used"],
        answer=agent_output["answer"],
        approval_required=agent_output["approval_required"],
        sources=agent_output.get("sources", []),
    )
