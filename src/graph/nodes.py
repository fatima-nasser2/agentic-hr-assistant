import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from src.graph.state import GraphState
from src.rag_pipeline import load_vectorstore

load_dotenv()

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

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(RouteDecision)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a router for an HR policy assistant at NovaTech Inc.
        
Your job is to decide whether a question can be answered from HR policy documents or not.

Route to 'rag' if the question is about:
- Leave and time off (sick days, annual leave, parental leave, etc.)
- Remote work and office policies
- Hiring and onboarding
- Compensation, salary, and benefits
- Code of conduct and workplace behavior
- Learning and development
- Any other HR or company policy topic

Route to 'unknown' if the question is about:
- Technical or engineering topics
- Personal advice unrelated to work policies
- Anything clearly outside the scope of HR policies

Be decisive. When in doubt, route to 'rag'."""),
        ("human", "Question: {question}")
    ])

    chain = prompt | structured_llm
    result = chain.invoke({"question": state["question"]})

    print(f"🔀 Router decision: {result.route} — {result.reasoning}")

    return {**state, "route": result.route}

# ── RAG NODE ─────────────────────────────────────────────
def rag_node(state: GraphState) -> GraphState:
    print("🔍 RAG Agent: retrieving relevant documents...")

    attempts = state.get("retrieval_attempts", 0)
    question = state["question"]

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    if attempts == 0:
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an expert at rewriting HR policy questions to improve document retrieval.\n"
             "Rewrite the question to be more specific, include relevant HR terminology, "
             "expand abbreviations, and make the intent crystal clear.\n"
             "Return ONLY the rewritten question, nothing else."),
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

    vectorstore = load_vectorstore()
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

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
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

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(ResponseOutput)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an HR policy assistant for NovaTech Inc.\n\n"
         "Answer the question using ONLY the provided policy excerpts.\n"
         "Do NOT use any outside knowledge.\n"
         "Be specific — include exact numbers, dates, or rules where available.\n"
         "If the excerpts do not contain a complete answer, say so clearly.\n\n"
         "Also list the source document filenames you drew from."),
        ("human", "Question: {question}\n\nPolicy excerpts:\n{documents}")
    ])

    chain = prompt | structured_llm
    result = chain.invoke({"question": question, "documents": formatted_docs})

    sources_line = ", ".join(result.sources) if result.sources else "HR Policy Documents"
    generation = f"{result.answer}\n\nSources: {sources_line}"

    print(f"💬 Response Agent: answer generated from {len(result.sources)} source(s)")

    return {**state, "generation": generation}

# ── UNKNOWN NODE ─────────────────────────────────────────
def unknown_node(state: GraphState) -> GraphState:
    print("❓ Unknown: question outside HR policy scope...")
    return {**state, "generation": "I don't have information about that in the HR policy documents."}