"""
models.py - Data models and Pydantic schemas for ShellSathi
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


@dataclass
class Record:
    """Linux command record representing a command and its example task."""
    command: str
    platform: str
    description: str
    example_task: str
    example_command: str
    source_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentChunk:
    """Indexed document chunk for vector similarity search."""
    chunk_id: str
    text: str
    source: str
    page: str
    title: str

    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "page": self.page,
            "title": self.title,
            "chunk_id": self.chunk_id,
        }

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["metadata"] = self.metadata
        return data


# --- Pydantic Schemas for FastAPI Endpoints ---

class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, description="Linux question")


class QuestionResponse(BaseModel):
    question: str
    total_results: int
    answer: str
    results: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    question: Optional[str] = Field(default=None, description="User question for AI chat")
    message: Optional[str] = Field(default=None, description="Alternative field for user message")


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    follow_up: str


class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Question for RAG system")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    confidence: float
    context_used: List[str] = Field(default_factory=list)


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, description="Question or task for the ShellSathi agent")
    approved: Optional[bool] = Field(default=False, description="User confirmation for destructive commands")


class AgentResponse(BaseModel):
    question: str
    intent: str
    tools_used: List[str]
    answer: str
    approval_required: bool
    sources: List[str] = Field(default_factory=list)
