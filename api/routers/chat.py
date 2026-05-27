import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from api.models import ChatRequest, ChatResponse, AgentTraceStep
from api.dependencies import get_current_employee
from src.graph.graph import build_graph

router = APIRouter(prefix="/chat", tags=["Chat"])

# Cache graph
_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_employee: dict = Depends(get_current_employee)
):
    """Send a question and get a full answer with agent trace."""
    graph = get_graph()
    thread_id = request.thread_id or str(uuid.uuid4())

    initial_state = {
        "question": request.question,
        "rewritten_question": "",
        "documents": [],
        "generation": "",
        "retrieval_attempts": 0,
        "relevance": "",
        "route": "",
        "retrieval_source": "",
        "chat_history": [],
        "employee_id": current_employee["employee_id"]
    }

    config = {"configurable": {"thread_id": thread_id}}

    # Stream events and collect trace
    agent_trace = []
    final_state = {}

    try:
        for event in graph.stream(initial_state, config=config):
            for node_name, node_output in event.items():
                final_state.update(node_output)

                if node_name == "router":
                    agent_trace.append(AgentTraceStep(
                        node="Router Agent",
                        decision=node_output.get("route"),
                        details="Classified question scope"
                    ))
                elif node_name == "source_router":
                    agent_trace.append(AgentTraceStep(
                        node="Source Router",
                        decision=node_output.get("retrieval_source"),
                        details="Selected retrieval source"
                    ))
                elif node_name == "rag":
                    agent_trace.append(AgentTraceStep(
                        node="RAG Agent",
                        decision=f"attempt #{node_output.get('retrieval_attempts')}",
                        details=node_output.get("rewritten_question", "")
                    ))
                elif node_name == "sql":
                    agent_trace.append(AgentTraceStep(
                        node="SQL Agent",
                        decision="queried database",
                        details=f"Retrieved data for {current_employee['employee_id']}"
                    ))
                elif node_name == "internal_kb":
                    agent_trace.append(AgentTraceStep(
                        node="Internal KB Agent",
                        decision="queried knowledge base",
                        details="Retrieved from internal knowledge base"
                    ))
                elif node_name == "grader":
                    agent_trace.append(AgentTraceStep(
                        node="Grader Agent",
                        decision=node_output.get("relevance"),
                        details="Scored chunk relevance"
                    ))
                elif node_name == "response":
                    agent_trace.append(AgentTraceStep(
                        node="Response Agent",
                        decision="generated",
                        details="Answer generated with citations"
                    ))
                elif node_name == "unknown":
                    agent_trace.append(AgentTraceStep(
                        node="Unknown Node",
                        decision="out of scope",
                        details="Question outside system scope"
                    ))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph execution failed: {str(e)}"
        )

    # Extract sources from answer
    generation = final_state.get("generation", "")
    sources = []
    if "Sources:" in generation:
        sources_line = generation.split("Sources:")[-1].strip()
        sources = [s.strip() for s in sources_line.split(",")]

    return ChatResponse(
        answer=generation,
        sources=sources,
        retrieval_source=final_state.get("retrieval_source", "unknown"),
        agent_trace=agent_trace,
        thread_id=thread_id,
        employee_id=current_employee["employee_id"]
    )