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
    token_usage: Optional[Dict[str, Any]] = Field(default=None, description="LLM token usage statistics")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Question for RAG system")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of context chunks to retrieve")


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[str]
    confidence: float
    context_used: List[str] = Field(default_factory=list)
    token_usage: Optional[Dict[str, Any]] = Field(default=None, description="LLM token usage statistics")


class AgentRequest(BaseModel):
    question: Optional[str] = Field(default="", description="Question or task for the ShellSathi agent")
    thread_id: Optional[str] = Field(default="default_user", description="Thread identifier for conversation memory")
    approved: Optional[bool] = Field(default=None, description="User confirmation (true=approve, false=reject)")


class AgentResponse(BaseModel):
    answer: str
    tool_used: str
    approval_required: bool
    thread_id: str
    question: Optional[str] = ""
    intent: Optional[str] = "general"
    tools_used: List[str] = Field(default_factory=list)
    status: Optional[str] = "COMPLETED"
    sources: List[str] = Field(default_factory=list)


# --- Day 10: User Feedback Schemas ---

class FeedbackRequest(BaseModel):
    question: str = Field(min_length=1, description="Question asked by the user")
    answer: str = Field(description="Answer provided by ShellSathi")
    rating: str = Field(description="'helpful' (thumbs up) or 'not_helpful' (thumbs down)")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp of submission")
    thread_id: Optional[str] = Field(default=None, description="Session thread identifier")


class FeedbackResponse(BaseModel):
    status: str
    message: str
    total_feedback: int
