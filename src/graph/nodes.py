import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from src.graph.state import GraphState
from src.rag_pipeline import load_vectorstore
from src.ingestion import HR_POLICIES_INDEX, INTERNAL_KB_INDEX
from src.database.query_engine import query_to_documents

load_dotenv()  # works locally
# On HF Spaces, OPENAI_API_KEY is set as environment variable automatically

# ── ROUTER NODE ──────────────────────────────────────────

class RouteDecision(BaseModel):
    """Structured output for routing decision"""
    route: str = Field(
        description="Route to take: 'rag' for HR questions, 'unknown' for everything else"
    )
    reasoning: str = Field(
        description="Brief reason for this routing decision"
    )

def router_node(state: GraphState) -> GraphState:
    print("🔀 Router: analyzing question...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=1)
    structured_llm = llm.with_structured_output(RouteDecision)

    chat_history = state.get("chat_history", [])
    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in chat_history[-4:]
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a router for an HR policy assistant at NovaTech Inc.

Your job is to decide whether a question is work-related or completely off-topic.

Route to 'rag' if the question is about ANY of these:
- Leave and time off (sick days, annual leave, parental leave, etc.)
- Remote work and office policies
- Hiring and onboarding
- Compensation, salary, and benefits
- Code of conduct and workplace behavior
- Learning and development
- Personal employee data (leave balance, salary, review dates)
- External HR topics, labor laws, or industry benchmarks
- Internal company information: team structure, org chart, leadership, tools, systems
- Onboarding, first-day guides, IT setup, software requests
- Any work or employment related topic

Route to 'unknown' ONLY if the question is completely unrelated to work:
- General knowledge questions (capitals, math, science)
- Personal advice unrelated to work
- Technical coding help unrelated to NovaTech systems
- Casual conversation with no work context

Be inclusive. When in doubt, route to 'rag'.
The Source Router will handle deciding exactly which data source to use.

Recent conversation:
{chat_history}

Use this history to interpret vague follow-up questions (e.g. "what about sick days?" after a leave question)."""),
        ("human", "Question: {question}")
    ])

    chain = prompt | structured_llm
    result = chain.invoke({"question": state["question"], "chat_history": history_text})

    print(f"🔀 Router decision: {result.route} — {result.reasoning}")

    return {**state, "route": result.route}

# ── SOURCE ROUTER NODE ───────────────────────────────────

class SourceDecision(BaseModel):
    """Structured output for source routing decision"""
    source: str = Field(
        description="Source to use: 'faiss' for HR policies, 'sql' for personal employee data, 'internal_kb' for internal company knowledge, 'web' for external information"
    )
    reasoning: str = Field(
        description="Brief explanation of why this source was chosen"
    )

def source_router_node(state: GraphState) -> GraphState:
    print("🗄️ Source Router: deciding retrieval source...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=1)
    structured_llm = llm.with_structured_output(SourceDecision)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a retrieval source router for NovaTech's HR Assistant.

Your job is to decide which data source to query based on the question.

Available sources:

1. 'faiss' — Vector store containing HR policy documents
   Use when the question is about:
   - Company policies (leave, remote work, hiring, compensation structure, code of conduct)
   - Rules, entitlements, and procedures that apply to ALL employees
   - How things work at NovaTech in general
   Examples:
   - "What is the sick leave policy?"
   - "How does the hiring process work?"
   - "What are the remote work rules?"

2. 'sql' — Relational database containing specific employee records
   Use when the question is about:
   - Personal data specific to an individual employee
   - Current balances, salaries, dates, and numbers tied to a specific person
   - Information that varies per employee
   Examples:
   - "How many sick days do I have left?"
   - "What is my current salary?"
   - "When is my next performance review?"
   - "How many annual leave days do I have remaining?"

3. 'internal_kb' — Internal company knowledge base
   Use when the question is about:
   - Company announcements and internal news
   - Team structure and org chart
   - Onboarding guides and new employee information
   - IT guidelines, tools, and internal systems
   Examples:
   - "Who is on the engineering team?"
   - "What tools does NovaTech use?"
   - "What should I do on my first day?"
   - "How do I set up my laptop?"
   - "What was announced at the last all-hands?"

4. 'web' — Live web search for external information
   Use when the question is about:
   - Current events or recent news
   - Information that is not in HR policies, employee records, or internal docs
   - Industry trends, legal changes, or external benchmarks
   Examples:
   - "What are the latest labor laws in Lebanon?"
   - "What is the average salary for an AI Engineer in 2026?"
   - "What are HR trends this year?"

Be decisive. When in doubt:
- Same for every employee and in policy docs → faiss
- Differs per employee → sql
- Internal company info, teams, tools, onboarding → internal_kb
- External / real-world information → web"""),
        ("human", "Question: {question}")
    ])

    chain = prompt | structured_llm
    result = chain.invoke({"question": state["question"]})

    print(f"🗄️ Source decision: {result.source} — {result.reasoning}")

    return {**state, "retrieval_source": result.source}

# ── SQL NODE ─────────────────────────────────────────────

def sql_node(state: GraphState) -> GraphState:
    print("🗃️ SQL Node: querying employee database...")

    employee_id = state.get("employee_id", "").strip()

    # If no employee ID provided, ask for it
    if not employee_id:
        print("🗃️ SQL Node: no employee ID found — requesting it")
        return {
            **state,
            "documents": [],
            "generation": "To look up your personal data, I need your employee ID. Please provide it in the format EMP001, EMP042, etc.",
        }

    # Query the database
    documents = query_to_documents(employee_id, state["question"])
    print(f"🗃️ SQL Node: retrieved data for employee {employee_id}")

    return {
        **state,
        "documents": documents,
        "rewritten_question": state["question"],
        "retrieval_attempts": state.get("retrieval_attempts", 0) + 1
    }

# ── RAG NODE ─────────────────────────────────────────────
def rag_node(state: GraphState) -> GraphState:
    print("🔍 RAG Agent: retrieving relevant documents...")

    attempts = state.get("retrieval_attempts", 0)
    question = state["question"]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=1)

    # ── Format chat history for context ──────────────────
    history = state.get("chat_history", [])
    history_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in history[-4:]
    ]) if history else "No previous conversation."

    if attempts == 0:
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert at rewriting HR policy questions to improve document retrieval.\n"
             "You have access to recent conversation history to resolve pronouns and references.\n"
             "Use the history to understand what 'them', 'it', 'this', 'that' refers to.\n"
             "Rewrite the question to be fully self-contained, specific, and retrieval-friendly.\n"
             "Return ONLY the rewritten question, nothing else.\n\n"
             f"Recent conversation:\n{history_text}"),
            ("human", "Original question: {question}")
        ])
    else:
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert at rewriting HR policy questions to improve document retrieval.\n"
             "This is a RETRY — the first search found no relevant documents.\n"
             "Rewrite the question using DIFFERENT keywords: try synonyms, related terms, "
             "and a broader scope to catch more relevant chunks.\n"
             "Return ONLY the rewritten question, nothing else."),
            ("human", "Original question: {question}")
        ])

    rewrite_chain = rewrite_prompt | llm | StrOutputParser()
    rewritten_question = rewrite_chain.invoke({"question": question})

    index_path = INTERNAL_KB_INDEX if state.get("retrieval_source") == "internal_kb" else HR_POLICIES_INDEX
    vectorstore = load_vectorstore(index_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    documents = retriever.invoke(rewritten_question)

    return {
        **state,
        "rewritten_question": rewritten_question,
        "documents": documents,
        "retrieval_attempts": attempts + 1,
        "generation": "",
    }

# ── GRADER NODE ──────────────────────────────────────────

class GradeDecision(BaseModel):
    """Structured output for relevance grading"""
    relevance: str = Field(
        description="'relevant' if the chunks contain enough information to answer the question, 'not_relevant' otherwise"
    )
    reasoning: str = Field(
        description="Brief explanation of the grading decision"
    )

def grader_node(state: GraphState) -> GraphState:
    print("⚖️  Grader: scoring document relevance...")

    question = state.get("rewritten_question") or state["question"]
    documents = state["documents"]

    if not documents:
        print("⚖️  Grader decision: not_relevant — no documents retrieved")
        return {**state, "relevance": "not_relevant"}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=1)
    structured_llm = llm.with_structured_output(GradeDecision)

    formatted_docs = "\n\n".join(
        f"[Chunk {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(documents)
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a strict relevance grader for an HR policy assistant.\n\n"
         "Decide whether the retrieved chunks contain enough information to answer the question.\n\n"
         "Grade as 'relevant' ONLY if the chunks directly address the question with specific details.\n"
         "Grade as 'not_relevant' if:\n"
         "- The chunks cover a different topic\n"
         "- The chunks are too vague or generic\n"
         "- Key details needed to answer are missing\n\n"
         "Be strict. A partial match is not enough."),
        ("human", "Question: {question}\n\nRetrieved chunks:\n{documents}")
    ])

    chain = prompt | structured_llm
    result = chain.invoke({"question": question, "documents": formatted_docs})

    print(f"⚖️  Grader decision: {result.relevance} — {result.reasoning}")

    return {**state, "relevance": result.relevance}

# ── RESPONSE NODE ────────────────────────────────────────

class ResponseOutput(BaseModel):
    """Structured output for the final answer"""
    answer: str = Field(
        description="Grounded answer based strictly on the retrieved policy documents"
    )
    sources: List[str] = Field(
        description="Filenames of the policy documents used to generate this answer"
    )

def response_node(state: GraphState) -> GraphState:
    print("💬 Response Agent: generating final answer...")

    if state.get("relevance") == "not_relevant":
        if state.get("generation"):
            print("💬 Response Agent: using upstream generation (e.g. SQL no-ID message)")
            return state
        print("💬 Response Agent: no relevant docs found — returning fallback")
        return {
            **state,
            "generation": (
                "I couldn't find specific information about that in the HR policy documents. "
                "Please contact the People Ops team for further assistance."
            ),
        }

    question = state.get("rewritten_question") or state["question"]
    documents = state["documents"]

    formatted_docs = "\n\n".join(
        f"[Source: {os.path.basename(doc.metadata.get('source', 'unknown'))}]\n{doc.page_content}"
        for doc in documents
    )

    chat_history = state.get("chat_history", [])
    history_text = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in chat_history[-4:]
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=30, max_retries=1)
    structured_llm = llm.with_structured_output(ResponseOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an HR policy assistant for NovaTech Inc.\n\n"
         "Answer the question using ONLY the provided policy excerpts.\n"
         "Do NOT use any outside knowledge.\n"
         "Be specific — include exact numbers, dates, or rules where available.\n"
         "If the excerpts do not contain a complete answer, say so clearly.\n\n"
         "Also list the source document filenames you drew from.\n\n"
         "Recent conversation:\n{chat_history}\n\n"
         "Use this history to give coherent follow-up answers (e.g. avoid repeating context already established)."),
        ("human", "Question: {question}\n\nPolicy excerpts:\n{documents}")
    ])

    chain = prompt | structured_llm
    result = chain.invoke({"question": question, "documents": formatted_docs, "chat_history": history_text})

    sources_line = ", ".join(result.sources) if result.sources else "HR Policy Documents"
    generation = f"{result.answer}\n\nSources: {sources_line}"

    print(f"💬 Response Agent: answer generated from {len(result.sources)} source(s)")

    return {**state, "generation": generation}

# ── UNKNOWN NODE ─────────────────────────────────────────
def unknown_node(state: GraphState) -> GraphState:
    print("❓ Unknown: question outside HR policy scope...")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, timeout=30, max_retries=1)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are the NovaTech HR Assistant.\n\n"
         "The user's message is not an HR policy question. Respond based on what it is:\n\n"
         "- If it is a greeting or small talk (e.g. 'hello', 'hi', 'how are you'), "
         "reply warmly, briefly introduce yourself, and invite them to ask an HR question.\n"
         "- If it is off-topic (e.g. coding help, general knowledge, personal advice), "
         "politely explain that you can only answer questions about NovaTech HR policies "
         "(leave, remote work, compensation, hiring, code of conduct).\n\n"
         "Keep your response short and friendly."),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": state["question"]})

    return {**state, "generation": response}