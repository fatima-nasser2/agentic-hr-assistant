---
title: NovaTech HR Assistant
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.41.0"
python_version: "3.10"
app_file: app/main.py
pinned: false
---

# NovaTech HR Assistant

[![Live Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/fatiman123/agentic-hr-assistant) [![React App](https://img.shields.io/badge/React-Live%20Demo-61dafb)](https://agentic-hr-assistant.vercel.app)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/Agents-LangGraph-orange)](https://github.com/langchain-ai/langgraph)
[![React](https://img.shields.io/badge/Frontend-React%2019-61dafb)](https://react.dev)

An intelligent, agentic HR chatbot that answers employee questions about company policies and personal HR data. Built on a **LangGraph state machine** with multi-source routing — it decides whether to query HR policy documents (FAISS), employee records (SQLite), internal knowledge base, or external sources, then grades the retrieved content before generating a source-cited answer. Every response is automatically evaluated for quality using an LLM-as-judge layer.

---

## Table of Contents

- [60-Second Overview](#60-second-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [API Reference](#api-reference)
- [Knowledge Base](#knowledge-base)
- [Evaluation Layer](#evaluation-layer)
- [Testing](#testing)
- [Deployment](#deployment)
- [Author](#author)

---

## 60-Second Overview

**What it does:** An employee asks "How many vacation days do I have left?" or "What's our remote work policy?" The system:

1. **Routes** the question — HR topic or off-topic?
2. **Selects a source** — personal employee data (SQL), HR policies (FAISS), company info (Internal KB), or web
3. **Retrieves** relevant content and **grades** its relevance (retries with synonym expansion if it fails)
4. **Generates** a grounded, source-cited answer
5. **Evaluates** the answer quality automatically (groundedness, relevance, completeness)

**Who uses it:** Employees authenticate with their employee ID, then chat in a React frontend or Streamlit demo. The FastAPI backend maintains conversation history per session and exposes a streaming endpoint for real-time responses.

---

## Architecture

### Agent Graph

```
User Question
      │
      ▼
┌──────────────┐
│ router_node  │ ── "unknown" ──────────────────────────► unknown_node ──► END
└──────┬───────┘                                            (friendly redirect)
       │ "rag"
       ▼
┌────────────────────┐
│ source_router_node │ ── selects: "faiss" | "sql" | "internal_kb" | "web"
└──────┬─────────────┘
       │
       ├── "sql"  ──────────────────────────────────────► sql_node
       │                                                      │
       └── "faiss" / "internal_kb" ──────────────────► rag_node
                                                             │
                                                             ▼
                                                      ┌──────────────┐
                                                      │ grader_node  │
                                                      └──────┬───────┘
                                                             │
                                          "relevant" ────────┤
                                                             │
                          "not_relevant" + attempts < 2 ─────┤──► rag_node (retry)
                                                             │
                          "not_relevant" + attempts ≥ 2 ─────┤
                                                             │
                                                             ▼
                                                      response_node ──► END
                                                    (grounded answer + sources)
```

### Nodes

| Node | Model | Role |
|------|-------|------|
| `router_node` | GPT-4o mini (temp=0) | Binary classify: `"rag"` (HR topic) or `"unknown"` (out of scope); uses chat history for vague follow-ups |
| `source_router_node` | GPT-4o mini (temp=0) | Selects retrieval source: `"faiss"`, `"sql"`, `"internal_kb"`, or `"web"` |
| `rag_node` | GPT-4o mini + FAISS (temp=0) | Rewrites question for retrieval, queries FAISS (k=4 chunks), tracks attempt count |
| `sql_node` | SQLite | Queries employee records (leave balances, salary, review dates) by employee ID |
| `grader_node` | GPT-4o mini (temp=0) | Strict relevance check — partial matches fail; triggers retry on failure |
| `response_node` | GPT-4o mini (temp=0) | Generates grounded answer from retrieved docs with source filenames appended |
| `unknown_node` | GPT-4o mini (temp=0.3) | Friendly scoped response for greetings, off-topic, and small talk |

### State

```python
class GraphState(TypedDict):
    question: str               # Original user input
    rewritten_question: str     # Retrieval-optimized query
    documents: List[Document]   # Retrieved chunks
    generation: str             # Final answer text
    retrieval_attempts: int     # Retry counter (max 2)
    relevance: str              # "relevant" | "not_relevant"
    route: str                  # "rag" | "unknown"
    retrieval_source: str       # "faiss" | "sql" | "internal_kb" | "web"
    chat_history: List[dict]    # Session context (last 4 turns)
    employee_id: str            # For SQL queries and personalization
```

---

## Features

- **Multi-Source Routing** — Intelligently routes to HR policies (FAISS), personal employee data (SQL), internal company info (Internal KB), or web based on the question type
- **Query Rewriting** — Optimizes raw user input for vector search; expands with synonyms on retries
- **Adaptive Retrieval** — Up to 2 retrieval attempts; retries with broader terms if relevance check fails
- **Relevance Grading** — Strict LLM evaluation of retrieved chunks before response generation
- **Source-Cited Answers** — Every response references the exact document(s) it was derived from
- **Conversation Memory** — Session-based history (4 turns) for coherent follow-ups; resolves pronouns
- **JWT Authentication** — Employees log in with their employee ID; 8-hour token expiry
- **Streaming Responses** — SSE endpoint streams trace steps and answer tokens in real-time
- **Agent Trace UI** — React frontend and Streamlit app both visualize node execution and routing decisions
- **LLM-as-Judge Evaluation** — Async quality scoring (groundedness, relevance, completeness) stored in SQLite
- **Human Feedback** — Thumbs up/down ratings with optional comments, linked to evaluation records
- **Graceful Fallbacks** — Clear messages for greetings, off-topic queries, missing personal data, and retrieval failures

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph |
| LLM | OpenAI GPT-4o mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | FAISS (local, CPU) |
| LLM Framework | LangChain, LangChain-Community |
| Backend API | FastAPI (async, with lifespan) |
| Frontend | React 19, Vite, TailwindCSS |
| Demo App | Streamlit |
| Database | SQLite (employees, evaluations, feedback) |
| Auth | JWT (python-jose) |
| Language | Python 3.10+ / JavaScript |
| Container | Docker (multi-stage build) |
| Deployment | Railway, Hugging Face Spaces |

---

## Project Structure

```
agentic-hr-assistant/
├── api/                          # FastAPI REST API
│   ├── main.py                   # App entry point, CORS, lifespan
│   ├── models.py                 # Pydantic request/response schemas
│   ├── dependencies.py           # JWT auth, token creation
│   └── routers/
│       ├── auth.py               # POST /auth/login
│       ├── chat.py               # POST /chat, POST /chat/stream
│       ├── feedback.py           # POST /feedback
│       └── sources.py            # GET /sources
│
├── src/                          # Core Python modules
│   ├── graph/
│   │   ├── state.py              # GraphState TypedDict
│   │   ├── nodes.py              # All agent node implementations
│   │   └── graph.py              # LangGraph builder & conditional routing
│   ├── ingestion.py              # Document loading, chunking, FAISS indexing
│   ├── rag_pipeline.py           # Vector store loading (cached) & retrieval utils
│   ├── test_graph.py             # Test suite
│   ├── database/
│   │   ├── query_engine.py       # SQLite queries for employee data & evaluations
│   │   └── setup_db.py           # DB init with 50 synthetic employees
│   └── evaluation/
│       └── evaluator.py          # LLM-as-judge async quality scoring
│
├── app/
│   └── main.py                   # Streamlit demo with real-time agent trace
│
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/           # Auth, chat, layout components
│   │   ├── hooks/                # Custom React hooks
│   │   └── services/             # API client, auth service
│   └── package.json
│
├── data/
│   ├── raw/
│   │   ├── hr_policies/          # 5 source HR policy documents
│   │   └── internal_kb/          # 4 internal company documents
│   ├── processed/
│   │   ├── faiss_hr_policies/    # Pre-built FAISS index
│   │   └── faiss_internal_kb/    # Pre-built FAISS index
│   └── hr_database.db            # SQLite: employees, leave_balances, payroll, evaluations
│
├── Dockerfile                    # Multi-stage build (ingest → API server)
├── Procfile                      # Railway: uvicorn api.main:app
├── railway.json                  # Railway deployment config
├── requirements.txt              # Python dependencies
└── .env                          # OPENAI_API_KEY, JWT_SECRET_KEY
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 16+ (for React frontend only)
- OpenAI API key

### Option A — Streamlit Demo (Simplest)

```bash
git clone https://github.com/fatima-nasser2/agentic-hr-assistant.git
cd agentic-hr-assistant

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env
echo "OPENAI_API_KEY=sk-..." > .env

# Ingest documents (one-time; skip if using pre-built indexes)
python src/ingestion.py

streamlit run app/main.py
# Open http://localhost:8501
```

### Option B — FastAPI Backend + React Frontend

**Backend:**
```bash
# Same setup as above, then:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
# Swagger UI: http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Option C — Docker

```bash
docker build --build-arg OPENAI_API_KEY="sk-..." -t hr-assistant .
docker run -p 8000:8000 hr-assistant
```

### Environment Variables

```env
OPENAI_API_KEY=sk-...                          # Required
JWT_SECRET_KEY=your-secret-key                 # Optional (has default)
```

---

## API Reference

All endpoints except `/health` and `/auth/login` require a `Bearer` token.

### Authentication

```
POST /auth/login
Body:     { "employee_id": "EMP001" }
Response: { "access_token": "...", "token_type": "bearer", "employee_id": "EMP001", "name": "..." }
```

### Chat

```
POST /chat
Headers:  Authorization: Bearer <token>
Body:     { "question": "...", "thread_id": "...", "chat_history": [...] }
Response: {
  "answer": "...",
  "sources": ["leave_policy.txt"],
  "retrieval_source": "faiss",
  "agent_trace": [{ "node": "router_node", "decision": "rag", ... }],
  "evaluation": { "groundedness": 4.5, "relevance": 5.0, "completeness": 4.0, "overall": 4.5 },
  "chat_history": [...]
}

POST /chat/stream
Same request; returns Server-Sent Events:
  { "type": "trace", "node": "...", "decision": "...", "details": "..." }
  { "type": "token", "value": "..." }
  { "type": "done", "sources": [...], "evaluation": {...} }
```

### Feedback

```
POST /feedback
Body: { "thread_id": "...", "question": "...", "answer": "...", "rating": "up|down", "comment": "...", "eval_id": "..." }
```

### Other

```
GET /sources   # Lists available knowledge bases
GET /health    # { "status": "ok", "version": "2.0.0" }
```

---

## Knowledge Base

### HR Policies (FAISS — `data/raw/hr_policies/`)

| Document | Contents |
|----------|----------|
| `leave_policy.txt` | Annual leave (21 days), sick leave (10 days), parental leave (16/4 weeks), bereavement, unpaid leave |
| `compensation_benefits.txt` | Salary benchmarking, merit increases (0–12%), bonuses, health/dental/vision, retirement (5% + 3% match), L&D budget ($1,500), wellness stipend ($600) |
| `hiring_policy.txt` | Internal-first posting (5 days), 4-stage interview process, offer timeline (3 working days), referral bonus |
| `remote_work_policy.txt` | Eligible roles, 2–4 days WFH, home office allowance ($500/yr), internet stipend ($30/mo) |
| `code_of_conduct.txt` | Anti-harassment, confidentiality, conflict of interest, disciplinary procedures, whistleblower protections |

### Internal Knowledge Base (FAISS — `data/raw/internal_kb/`)

Company announcements, team structure, onboarding guides, and IT tool documentation.

### Employee Database (SQLite)

51 synthetic employees across departments with:
- `employees` — name, email, department, job title, hire date, manager, status
- `leave_balances` — annual/sick days remaining, parental eligibility
- `payroll` — base salary, last bonus, last/next review date

Documents are chunked with `RecursiveCharacterTextSplitter` (chunk_size=500, overlap=100) and embedded using `text-embedding-3-small`.

---

## Evaluation Layer

After every vector search response (FAISS / Internal KB), the system asynchronously evaluates answer quality using GPT-4o mini in JSON mode:

| Dimension | Scale | Description |
|-----------|-------|-------------|
| Groundedness | 0–5 | Claims are supported by the retrieved context |
| Relevance | 0–5 | Answer directly addresses the question |
| Completeness | 0–5 | Key available information from context is included |
| Overall | 0–5 | Computed composite score |

Results are persisted to the `evaluations` table in SQLite and returned in the API response. Human feedback (thumbs up/down + comment) from the `/feedback` endpoint is linked to the same record via `eval_id`.

---

## Testing

```bash
python src/test_graph.py
```

Results are printed to console and saved to `outputs/test_results_<timestamp>.txt`.

The test suite covers:

| Category | Tests | What It Covers |
|----------|-------|----------------|
| Out of Scope | 5 | Greetings, general knowledge, non-HR topics |
| Vague Questions | 5 | Ambiguous or context-free inputs |
| Multi-Part Questions | 3 | Queries spanning multiple policies |
| Trick & Edge Cases | 7 | Hypotheticals, absurd requests, logical traps |
| Input Stress Tests | 4 | ALL CAPS, typos, slang, minimal punctuation |
| Prompt Injection | 2 | Attempts to override system instructions |
| Hallucination Bait | 2 | Requests for opinions or data not in documents |
| Sensitive Issues | 3 | Harassment, resignation, bullying |
| Missing Policies | 3 | Topics not in the knowledge base |
| Specific Detail Queries | 6 | Core RAG — leave days, bonuses, timelines, allowances |

Each test logs: routing decision, rewritten query, retrieval source, docs retrieved, relevance grade, and final answer.

---

## Deployment

### Railway

The project includes a `Procfile` and `railway.json` for one-command Railway deployment:

```bash
railway up
```

Set `OPENAI_API_KEY` as a Railway environment variable. The multi-stage Dockerfile builds FAISS indexes at image build time, so no cold-start ingestion is needed.

### Vercel (React Frontend)
The React frontend is deployed at [agentic-hr-assistant.vercel.app](https://agentic-hr-assistant.vercel.app).
Set `VITE_API_BASE` as a Vercel environment variable pointing to your Railway URL.

### Hugging Face Spaces

The Streamlit demo is deployed at [fatiman123/agentic-hr-assistant](https://huggingface.co/spaces/fatiman123/agentic-hr-assistant). Set `OPENAI_API_KEY` as a Space secret.

---

## Author

**Fatima Nasser**  
AI Engineer — LLMs, Agents, RAG, AI Automations

[LinkedIn](https://linkedin.com/in/fatima-nasser-ai) · [GitHub](https://github.com/fatima-nasser2)

---

## License

This project is licensed under the [MIT License](LICENSE).
