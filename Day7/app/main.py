"""
main.py - ShellSathi Day 7 FastAPI Application

Provides the core semantic search and vector database endpoints:
  - GET /search/semantic?q=...: Searches indexed Linux command chunks via persistent Chroma vector store.
  - GET /health: Healthcheck and index status.
  - GET /records: List curated ShellSathi command records.
  - GET /: Root welcome and API info.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from Day7.app.chunking import load_all_chunks
    from Day7.app.vectorstore import get_vector_store
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from Day7.app.chunking import load_all_chunks
    from Day7.app.vectorstore import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shellsathi.api")

app = FastAPI(
    title="ShellSathi AI API",
    description="Intelligent Linux Command Assistant with Chroma Vector Semantic Search",
    version="0.7.0",
)


class SemanticSearchResult(BaseModel):
    rank: int = Field(..., description="Hit rank order")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    distance: Optional[float] = Field(None, description="Cosine distance")
    source: str = Field(..., description="Original document source URL or file")
    page: str = Field(..., description="Command name / manual page")
    title: str = Field(..., description="Command task / operation title")
    text: str = Field(..., description="Document chunk text")


class SemanticSearchResponse(BaseModel):
    query: str
    total_hits: int
    results: List[SemanticSearchResult]


@app.on_event("startup")
async def startup_event() -> None:
    """Ensure vector store is initialized and documents are indexed on app startup."""
    try:
        store = get_vector_store()
        total = store.count()
        if total == 0:
            logger.info("Initializing and indexing ShellSathi chunks into Chroma...")
            store.index_chunks()
            logger.info("Startup indexing complete (%d chunks).", store.count())
        else:
            logger.info("Persistent Chroma vector store loaded with %d chunks.", total)
    except Exception as exc:
        logger.warning("Startup vector store initialization note: %s", exc)


@app.get("/", tags=["System"])
def root() -> Dict[str, Any]:
    """Root endpoint welcoming users and displaying API endpoints."""
    store = get_vector_store()
    return {
        "service": "ShellSathi Linux Assistant",
        "day": 7,
        "features": [
            "Document chunking with source, page, title metadata",
            "Dense semantic embeddings",
            "Persistent Chroma vector collection indexing",
            "Semantic search endpoint: /search/semantic?q=",
        ],
        "indexed_chunks": store.count(),
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
def health() -> Dict[str, Any]:
    """Return health status and Chroma index statistics."""
    store = get_vector_store()
    return {
        "status": "ok",
        "service": "ShellSathi",
        "version": "0.7.0",
        "vector_store": "Chroma",
        "collection": store.collection_name,
        "indexed_chunks": store.count(),
    }


@app.get("/search/semantic", response_model=SemanticSearchResponse, tags=["Search"])
def search_semantic(
    q: str = Query(..., min_length=1, description="Semantic search query (e.g. 'How can I display hidden files?')"),
    limit: int = Query(default=5, ge=1, le=50, description="Maximum number of hits to return"),
) -> SemanticSearchResponse:
    """
    Search indexed Linux command documents semantically using vector similarity.
    Returns ranked chunks with source, page, and title metadata.
    """
    clean_q = q.strip()
    if not clean_q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")

    store = get_vector_store()
    raw_hits = store.search(query=clean_q, top_k=limit)

    results = [
        SemanticSearchResult(
            rank=hit["rank"],
            chunk_id=hit["chunk_id"],
            score=hit["score"],
            distance=hit.get("distance"),
            source=hit["source"],
            page=hit["page"],
            title=hit["title"],
            text=hit["text"],
        )
        for hit in raw_hits
    ]

    return SemanticSearchResponse(
        query=clean_q,
        total_hits=len(results),
        results=results,
    )


@app.get("/records", tags=["Data"])
def list_records(
    limit: int = Query(default=10, ge=1, le=100, description="Max records to return"),
    command: Optional[str] = Query(default=None, description="Filter by command name (e.g. ls, grep, tar)"),
) -> Dict[str, Any]:
    """Retrieve raw ShellSathi command records."""
    chunks = load_all_chunks()
    if command:
        chunks = [c for c in chunks if c.page.lower() == command.lower()]

    formatted = [c.to_dict() for c in chunks[:limit]]
    return {
        "total": len(chunks),
        "returned": len(formatted),
        "records": formatted,
    }
