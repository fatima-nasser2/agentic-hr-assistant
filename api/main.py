import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, chat, feedback, sources
from src.database.query_engine import ensure_evaluations_table, ensure_hr_tables
from src.ingestion import (
    HR_POLICIES_RAW, INTERNAL_KB_RAW,
    HR_POLICIES_INDEX, INTERNAL_KB_INDEX,
    load_documents, chunk_documents, embed_and_store,
)

def _build_indexes_if_missing():
    for label, raw_path, index_path in [
        ("HR Policies", HR_POLICIES_RAW, HR_POLICIES_INDEX),
        ("Internal KB", INTERNAL_KB_RAW, INTERNAL_KB_INDEX),
    ]:
        if not os.path.exists(os.path.join(index_path, "index.faiss")):
            print(f"Building {label} FAISS index...")
            docs = load_documents(raw_path)
            chunks = chunk_documents(docs)
            embed_and_store(chunks, index_path)
            print(f"{label} index ready.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_hr_tables()
    ensure_evaluations_table()
    await asyncio.to_thread(_build_indexes_if_missing)
    yield

app = FastAPI(
    lifespan=lifespan,
    title="NovaTech HR Assistant API",
    description="""
## Agentic RAG HR Assistant

A production-grade multi-source RAG system powered by **LangGraph**, **FAISS**, **SQLite**, and **OpenAI GPT-4o mini**.

### How It Works
1. **Authenticate** — call `/auth/login` with your employee ID to get a JWT token
2. **Ask questions** — use `/chat` or `/chat/stream` with your token
3. **Give feedback** — rate answers with `/feedback`

### Retrieval Sources
| Source | What It Contains |
|--------|-----------------|
| 🗂️ HR Policies (FAISS) | Leave, remote work, hiring, compensation, code of conduct |
| 🗃️ Employee Database (SQL) | Personal leave balances, salary, review dates |
| 📚 Internal Knowledge Base | Announcements, team structure, onboarding, IT guidelines |

### Agent Pipeline
Every question passes through a **4-agent LangGraph pipeline**:
`Router → Source Router → Retrieval → Grader → Response`

### Authentication
All endpoints except `/auth/login` and `/health` require a Bearer token.
Include it in the Authorization header: `Bearer <your_token>`
    """,
    version="2.0.0",
    contact={
        "name": "Fatima — AI Engineer",
        "url": "https://linkedin.com/in/your-profile",
    },
    license_info={
        "name": "MIT License",
    }
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://agentic-hr-assistant.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ──────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(sources.router)

# ── HEALTH ───────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    """Check if the API is running and healthy."""
    return {"status": "ok", "version": "2.0.0"}