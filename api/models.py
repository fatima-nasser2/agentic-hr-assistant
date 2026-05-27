from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# ── AUTH ─────────────────────────────────────────────────

class LoginRequest(BaseModel):
    employee_id: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee_id: str
    name: str

# ── CHAT ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)
    thread_id: Optional[str] = None  # for conversation memory

class AgentTraceStep(BaseModel):
    node: str
    decision: Optional[str] = None
    details: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    retrieval_source: str
    agent_trace: List[AgentTraceStep]
    thread_id: str
    employee_id: str

# ── FEEDBACK ─────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    thread_id: str
    question: str
    answer: str
    rating: Literal["up", "down"]
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    message: str
    feedback_id: str

# ── SOURCES ──────────────────────────────────────────────

class SourceInfo(BaseModel):
    id: str
    name: str
    description: str
    document_count: int

class SourcesResponse(BaseModel):
    sources: List[SourceInfo]