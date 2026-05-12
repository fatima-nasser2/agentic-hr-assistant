from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.graph.state import GraphState

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
    # Tomorrow: real retrieval + query rewriting
    return {**state, "documents": [], "generation": ""}

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