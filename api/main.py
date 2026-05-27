from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, chat, feedback, sources

app = FastAPI(
    title="NovaTech HR Assistant API",
    description="Agentic RAG HR Assistant powered by LangGraph",
    version="2.0.0"
)

# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
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
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "2.0.0"}