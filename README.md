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

[![Live Demo](https://img.shields.io/badge/🤗%20Hugging%20Face-Live%20Demo-blue)](https://huggingface.co/spaces/fatiman123/agentic-hr-assistant)

An intelligent, agentic HR policy chatbot built with **LangGraph** and **Streamlit**. It answers employee questions about company policies using Retrieval-Augmented Generation (RAG), with automatic query routing, multi-attempt retrieval, relevance grading, and source-cited responses — all powered by OpenAI GPT-4o mini.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
  - [Agent Graph](#agent-graph)
  - [Nodes](#nodes)
  - [State](#state)
- [Knowledge Base](#knowledge-base)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
  - [1. Ingest Policy Documents](#1-ingest-policy-documents)
  - [2. Run the Web App](#2-run-the-web-app)
  - [3. Run the Test Suite](#3-run-the-test-suite)
- [Testing](#testing)
- [Example Interactions](#example-interactions)
- [License](#license)

---

## Overview

The NovaTech HR Assistant is a multi-agent RAG system that helps employees get accurate answers to HR policy questions. Instead of a single-pass LLM call, it uses a **LangGraph state machine** with specialized nodes for routing, retrieval, grading, and response generation — ensuring answers are always grounded in official policy documents with clear source attribution.

---

## Features

- **Intelligent Query Routing** — Distinguishes HR policy questions from off-topic queries before retrieval
- **Query Rewriting** — Rewrites user questions into retrieval-optimized search terms
- **Adaptive Retrieval** — Retries with synonym-expanded queries if the first retrieval fails relevance checks
- **Relevance Grading** — Evaluates whether retrieved chunks actually answer the question before generating a response
- **Source-Cited Answers** — Every response references the exact policy document(s) it was derived from
- **Conversation History** — Maintains session context so follow-up questions work naturally
- **Agent Trace UI** — Real-time visualization of which node is executing and why
- **Graceful Fallbacks** — Handles greetings, off-topic queries, and unanswerable questions with helpful redirects

---

## Architecture

### Agent Graph

```
User Question
      │
      ▼
┌─────────────┐
│ router_node │ ──── "unknown" ──────────────────────► unknown_node ──► END
└──────┬──────┘                                            (friendly redirect)
       │ "rag"
       ▼
┌─────────────┐
│   rag_node  │  (rewrite question → retrieve k=4 chunks → increment attempt)
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ grader_node  │
└──────┬───────┘
       │
       ├── "relevant" ──────────────────────────────► response_node ──► END
       │                                               (grounded answer + sources)
       │
       ├── "not_relevant" + attempts < 2 ──────────► rag_node (retry w/ synonyms)
       │
       └── "not_relevant" + attempts ≥ 2 ──────────► response_node ──► END
                                                       (fallback message)
```

### Nodes

| Node | Model | Role |
|------|-------|------|
| `router_node` | GPT-4o mini (temp=0) | Classifies query as `"rag"` (HR topic) or `"unknown"` (out of scope), using recent chat history for context |
| `rag_node` | GPT-4o mini (temp=0) | Rewrites the question for retrieval, queries the FAISS vector store (k=4), and tracks attempt count |
| `grader_node` | GPT-4o mini (temp=0) | Strictly evaluates whether retrieved documents answer the question; partial matches fail |
| `response_node` | GPT-4o mini (temp=0) | Generates a grounded answer using only retrieved policy excerpts, with source filenames appended |
| `unknown_node` | GPT-4o mini (temp=0.3) | Returns a friendly, scoped response for greetings, off-topic questions, or small talk |

### State

The graph passes a `GraphState` TypedDict between nodes:

```python
class GraphState(TypedDict):
    question: str                  # Original user input
    rewritten_question: str        # Retrieval-optimized query
    documents: List[Document]      # Retrieved policy chunks
    generation: str                # Final answer text
    retrieval_attempts: int        # Retry counter (max 2)
    relevance: str                 # "relevant" | "not_relevant"
    route: str                     # "rag" | "unknown"
    chat_history: List[dict]       # Session conversation history
```

---

## Knowledge Base

Five HR policy documents are embedded into a local FAISS vector store:

| Document | Contents |
|----------|----------|
| `leave_policy.txt` | Annual leave (21 days), sick leave (10 days), parental leave (16/4 weeks), bereavement, unpaid leave |
| `compensation_benefits.txt` | Salary benchmarking, merit increases (0–12%), bonuses, health/dental/vision, retirement (5% + 3% match), L&D budget (`$`1,500), wellness stipend ($600) |
| `hiring_policy.txt` | Internal-first posting (5 days), 4-stage interview process, offer timeline (3 working days), referral bonus |
| `remote_work_policy.txt` | Eligible roles, 2–4 days WFH, home office allowance (`$`500/yr), internet stipend ($30/mo) |
| `code_of_conduct.txt` | Anti-harassment, confidentiality, conflict of interest, disciplinary procedures, whistleblower protections |

Documents are chunked with `RecursiveCharacterTextSplitter` and embedded using OpenAI `text-embedding-3-small`.

---

## Tech Stack

| Category | Technology |
|----------|-----------|
| Agent Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | OpenAI GPT-4o mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | FAISS (local) |
| LLM Framework | LangChain |
| Web UI | Streamlit |
| Language | Python 3.10+ |

---

## Project Structure

```
agentic-hr-assistant/
├── app/
│   └── main.py                   # Streamlit web application
├── src/
│   ├── graph/
│   │   ├── state.py              # GraphState TypedDict
│   │   ├── nodes.py              # All agent node implementations
│   │   └── graph.py              # LangGraph builder & conditional routing
│   ├── ingestion.py              # Document loading, chunking, and embedding
│   ├── rag_pipeline.py           # Vector store loading & RAG chain setup
│   └── test_graph.py             # Comprehensive test suite (40 test cases)
├── data/
│   ├── raw/                      # Source HR policy .txt files
│   └── processed/
│       └── faiss_index/          # Pre-built FAISS vector store
├── outputs/                      # Timestamped test result logs
├── .env                          # OPENAI_API_KEY
└── .gitignore
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/fatima-nasser2/agentic-hr-assistant.git
cd agentic-hr-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install langchain langchain-openai langchain-community langchain-text-splitters \
            langgraph faiss-cpu streamlit python-dotenv pydantic openai
```

### 4. Configure your API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...your-key-here...
```

---

## Usage

### 1. Ingest Policy Documents

Run this once to chunk, embed, and store the HR policy documents in FAISS:

```bash
python src/ingestion.py
```

This reads files from `data/raw/` and writes the vector index to `data/processed/faiss_index/`.

### 2. Run the Web App

```bash
streamlit run app/main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. The UI provides:

- **Chat interface** — type any HR question in the input box
- **Agent trace panel** — real-time display of node execution and routing decisions
- **Sidebar** — knowledge base overview and clear chat button

### 3. Run the Test Suite

```bash
python src/test_graph.py
```

Results are printed to the console and saved to `outputs/test_results_<timestamp>.txt`.

---

## Testing

The test suite covers 40 test cases across 10 categories:

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
| Missing Policies | 3 | Topics not present in the knowledge base |
| Specific Detail Queries | 6 | Core RAG — leave days, bonuses, timelines, allowances |

Each test logs the routing decision, rewritten query, number of docs retrieved, relevance grade, and final answer.

---

## Example Interactions

**HR policy question:**
```
User:   How many sick days do I get per year?
Route:  rag
Grade:  relevant
Answer: Employees receive 10 sick days per year. These are non-cumulative
        and cannot be carried over to the next year.

        Sources: leave_policy.txt
```

**Follow-up using chat history:**
```
User:   What about parental leave?
Route:  rag  (context resolved from prior turn)
Answer: The primary caregiver receives 16 weeks of fully paid parental
        leave. Secondary caregivers receive 4 weeks of paid leave.

        Sources: leave_policy.txt
```

**Out-of-scope question:**
```
User:   Can you write me a Python script?
Route:  unknown
Answer: I'm NovaTech's HR Assistant and can only help with questions about
        company policies such as leave, remote work, compensation, hiring,
        and code of conduct. Is there anything HR-related I can help you with?
```

---

## Author

**Fatima**
AI Engineer — LLMs, Agents, RAG, AI Automations

[LinkedIn](https://linkedin.com/in/fatima-nasser-ai) · [GitHub](https://github.com/fatima-nasser2)

---

## License

This project is licensed under the [MIT License](LICENSE).
