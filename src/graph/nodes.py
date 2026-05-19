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
def grader_node(state: GraphState) -> GraphState:
    print("⚖️ Grader: checking relevance of retrieved documents...")
    # Tomorrow: real grading logic
    return {**state, "relevance": "relevant"}

# ── RESPONSE NODE ────────────────────────────────────────
def response_node(state: GraphState) -> GraphState:
    print("💬 Response Agent: generating final answer...")
    # Tomorrow: real answer generation
    return {**state, "generation": "This is a placeholder answer."}

# ── UNKNOWN NODE ─────────────────────────────────────────
def unknown_node(state: GraphState) -> GraphState:
    print("❓ Unknown: question outside HR policy scope...")
    return {**state, "generation": "I don't have information about that in the HR policy documents."}