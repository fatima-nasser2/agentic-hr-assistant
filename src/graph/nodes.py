from src.graph.state import GraphState

# ── ROUTER NODE ──────────────────────────────────────────
def router_node(state: GraphState) -> GraphState:
    print("🔀 Router: deciding how to handle question...")
    # Tomorrow: real routing logic
    return {**state, "route": "rag"}

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