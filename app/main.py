import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.graph.graph import build_graph
from src.ingestion import load_documents, chunk_documents, embed_and_store

# ── PAGE CONFIG ──────────────────────────────────────────
st.set_page_config(
    page_title="NovaTech HR Assistant",
    page_icon="🤖",
    layout="wide"
)

# Auto-build FAISS index if it doesn't exist
FAISS_PATH = "data/processed/faiss_index"
if not os.path.exists(FAISS_PATH):
    with st.spinner("Building knowledge base for first time... (this takes ~30 seconds)"):
        docs = load_documents("data/raw")
        chunks = chunk_documents(docs)
        embed_and_store(chunks, FAISS_PATH)

# ── CACHE GRAPH (build once per session) ─────────────────
@st.cache_resource
def get_graph():
    return build_graph()

# ── HEADER ───────────────────────────────────────────────
st.title("🤖 NovaTech HR Assistant")
st.caption("Powered by Agentic RAG — LangGraph + FAISS + GPT-4o mini")
st.divider()

# ── LAYOUT: two columns ──────────────────────────────────
col1, col2 = st.columns([1.2, 0.8])

with col2:
    st.subheader("🧠 Agent Trace")

# ── LEFT COLUMN: Chat ────────────────────────────────────
with col1:
    st.subheader("💬 Ask a Question")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown(
                "👋 Hi! I'm the **NovaTech HR Assistant**. I can answer questions about:\n\n"
                "- 🏖️ Leave & time-off policies\n"
                "- 🏠 Remote work & hybrid arrangements\n"
                "- 💰 Compensation & benefits\n"
                "- 🤝 Hiring & onboarding\n"
                "- 📋 Code of conduct\n\n"
                "How can I help you today?"
            )

    if question := st.chat_input("Ask about HR policies..."):

        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        initial_state = {
            "question": question,
            "rewritten_question": "",
            "documents": [],
            "generation": "",
            "retrieval_attempts": 0,
            "relevance": "",
            "route": "",
            "chat_history": st.session_state.chat_history
        }

        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        # ── RIGHT COLUMN: stream agent trace ─────────────
        with col2:
            with st.spinner("Agents working..."):
                graph = get_graph()
                final_state = {}

                for event in graph.stream(initial_state, config=config):
                    for node_name, node_output in event.items():
                        final_state.update(node_output)

                        if node_name == "router":
                            route = node_output.get("route", "unknown")
                            with st.status(f"🔀 Router Agent — routed to: `{route}`", state="complete"):
                                st.write(f"**Decision:** `{route}`")

                        elif node_name == "rag":
                            attempts = node_output.get("retrieval_attempts", 1)
                            rewritten = node_output.get("rewritten_question", "")
                            docs = node_output.get("documents", [])
                            with st.status(f"🔍 RAG Agent — attempt #{attempts}", state="complete"):
                                with st.expander("View rewritten query"):
                                    st.write(rewritten)
                                st.write(f"**Chunks retrieved:** {len(docs)}")

                        elif node_name == "grader":
                            relevance = node_output.get("relevance", "")
                            status_state = "complete" if relevance == "relevant" else "error"
                            with st.status(f"⚖️ Grader Agent — {relevance}", state=status_state):
                                st.write(f"**Relevance:** `{relevance}`")

                        elif node_name == "response":
                            with st.status("💬 Response Agent — generating answer", state="complete"):
                                st.write("Answer generated with citations.")

                        elif node_name == "unknown":
                            with st.status("❓ Unknown — out of scope", state="error"):
                                st.write("Question is outside HR policy scope.")

        # ── Display final answer ──────────────────────────
        final_answer = final_state.get("generation", "I encountered an error processing your request.")
        with col1:
            with st.chat_message("assistant"):
                st.markdown(final_answer)
            st.session_state.messages.append({"role": "assistant", "content": final_answer})
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.chat_history.append({"role": "assistant", "content": final_answer})

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **NovaTech HR Assistant** is an Agentic RAG system built with:
    - 🔗 **LangGraph** — agent orchestration
    - 🔍 **FAISS** — vector search
    - 🧠 **GPT-4o mini** — reasoning
    - 📄 **LangChain** — document processing
    """)

    st.divider()
    st.header("🗂️ Knowledge Base")
    st.markdown("""
    - Leave Policy
    - Remote Work Policy
    - Hiring Policy
    - Compensation & Benefits
    - Code of Conduct
    """)

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
