from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.graph.nodes import (
    router_node,
    rag_node,
    grader_node,
    response_node,
    unknown_node
)

# ── ROUTING FUNCTIONS ────────────────────────────────────
def route_question(state: GraphState) -> str:
    """After router node — decide which path to take"""
    if state["route"] == "rag":
        return "rag"
    return "unknown"

def check_relevance(state: GraphState) -> str:
    """After grader node — decide whether to respond or retry"""
    if state["relevance"] == "relevant":
        return "response"
    if state["retrieval_attempts"] >= 2:
        return "response"  # Stop retrying after 2 attempts
    return "retry"

# ── BUILD GRAPH ──────────────────────────────────────────
def build_graph():
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("grader", grader_node)
    graph.add_node("response", response_node)
    graph.add_node("unknown", unknown_node)

    # Entry point
    graph.set_entry_point("router")

    # Edges
    graph.add_conditional_edges(
        "router",
        route_question,
        {
            "rag": "rag",
            "unknown": "unknown"
        }
    )

    graph.add_edge("rag", "grader")

    graph.add_conditional_edges(
        "grader",
        check_relevance,
        {
            "response": "response",
            "retry": "rag"
        }
    )

    graph.add_edge("response", END)
    graph.add_edge("unknown", END)

    return graph.compile()