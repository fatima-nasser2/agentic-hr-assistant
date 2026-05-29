from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# ── AUTH ─────────────────────────────────────────────────

class LoginRequest(BaseModel):
    employee_id: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"employee_id": "EMP000"}]
        }
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee_id: str
    name: str
    
# ── CHAT HISTORY ─────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# ── CHAT ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)
    thread_id: Optional[str] = None  # for conversation memory
    chat_history: Optional[List[ChatMessage]] = []
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "How many sick days do I have left?",
                    "thread_id": None,
                    "chat_history": []
                }
            ]
        }
    }

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
    chat_history: List[ChatMessage]

# ── FEEDBACK ─────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    thread_id: str
    question: str
    answer: str
    rating: Literal["up", "down"]
    comment: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "thread_id": "abc-123",
                    "question": "How many sick days do I have left?",
                    "answer": "You have 2 sick days left.",
                    "rating": "up",
                    "comment": "Very helpful!"
                }
            ]
        }
    }

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