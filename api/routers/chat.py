import asyncio
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from api.models import ChatRequest, ChatResponse, AgentTraceStep, ChatMessage, EvaluationScores
from api.dependencies import get_current_employee
from src.graph.graph import build_graph
from src.evaluation.evaluator import evaluate_answer
from src.database.query_engine import save_evaluation

router = APIRouter(prefix="/chat", tags=["Chat"])

_graph = None

def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph

# ── SHARED HELPERS ───────────────────────────────────────

def _build_trace_step(node_name: str, node_output: dict, employee_id: str) -> AgentTraceStep | None:
    if node_name == "router":
        return AgentTraceStep(node="router", decision=node_output.get("route"), details="Classified question scope")
    if node_name == "source_router":
        return AgentTraceStep(node="source_router", decision=node_output.get("retrieval_source"), details="Selected retrieval source")
    if node_name == "rag":
        return AgentTraceStep(node="rag", decision=f"attempt #{node_output.get('retrieval_attempts')}", details=node_output.get("rewritten_question", ""))
    if node_name == "sql":
        return AgentTraceStep(node="sql", decision="queried database", details=f"Retrieved data for {employee_id}")
    if node_name == "internal_kb":
        return AgentTraceStep(node="internal_kb", decision="searched knowledge base", details=node_output.get("rewritten_question", ""))
    if node_name == "grader":
        return AgentTraceStep(node="grader", decision=node_output.get("relevance"), details="Scored chunk relevance")
    if node_name == "response":
        return AgentTraceStep(node="response", decision="generated", details="Answer generated with citations")
    if node_name == "unknown":
        return AgentTraceStep(node="unknown", decision="out of scope", details="Question outside system scope")
    return None

def _parse_sources(generation: str) -> list[str]:
    if "Sources:" not in generation:
        return []
    sources_line = generation.split("Sources:")[-1].strip()
    return [s.strip() for s in sources_line.split(",")]

async def _run_and_save_evaluation(
    question: str,
    answer: str,
    documents: list,
    retrieval_source: str,
    employee_id: str,
    thread_id: str,
) -> dict | None:
    """Run evaluation and persist to DB. Returns the scores dict or None."""
    scores = await evaluate_answer(question, answer, documents, retrieval_source)
    if not scores:
        return None
    eval_id = save_evaluation(
        employee_id=employee_id,
        thread_id=thread_id,
        question=question,
        answer=answer,
        retrieval_source=retrieval_source,
        groundedness=scores["groundedness"],
        relevance=scores["relevance"],
        completeness=scores["completeness"],
        overall=scores["overall"],
        reasoning=scores["reasoning"],
    )
    scores["eval_id"] = eval_id
    return scores

# ── /chat (full response) ────────────────────────────────

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_employee: dict = Depends(get_current_employee)
):
    graph = get_graph()
    thread_id = request.thread_id or str(uuid.uuid4())
    employee_id = current_employee["employee_id"]

    initial_state = {
        "question": request.question,
        "rewritten_question": "",
        "documents": [],
        "generation": "",
        "retrieval_attempts": 0,
        "relevance": "",
        "route": "",
        "retrieval_source": "",
        "chat_history": [
            {"role": msg.role, "content": msg.content}
            for msg in (request.chat_history or [])
        ],
        "employee_id": employee_id
    }

    config = {"configurable": {"thread_id": thread_id}}
    agent_trace = []
    final_state = {}

    try:
        async for event in graph.astream(initial_state, config=config):
            for node_name, node_output in event.items():
                final_state.update(node_output)
                step = _build_trace_step(node_name, node_output, employee_id)
                if step:
                    agent_trace.append(step)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    generation = final_state.get("generation", "")
    retrieval_source = final_state.get("retrieval_source", "")
    documents = final_state.get("documents", [])

    updated_history = list(request.chat_history or [])
    updated_history.append(ChatMessage(role="user", content=request.question))
    updated_history.append(ChatMessage(role="assistant", content=generation))

    # Run evaluation for answered questions (not off-topic)
    evaluation = None
    if final_state.get("route") == "rag" and generation and retrieval_source:
        try:
            scores = await asyncio.wait_for(
                _run_and_save_evaluation(
                    request.question, generation, documents,
                    retrieval_source, employee_id, thread_id,
                ),
                timeout=15.0,
            )
            if scores:
                evaluation = EvaluationScores(**scores)
        except asyncio.TimeoutError:
            print("[Evaluation] Timed out after 15s, skipping")

    return ChatResponse(
        answer=generation,
        sources=_parse_sources(generation),
        retrieval_source=retrieval_source,
        agent_trace=agent_trace,
        thread_id=thread_id,
        employee_id=employee_id,
        chat_history=updated_history,
        evaluation=evaluation,
    )

# ── /chat/stream (streaming response) ───────────────────

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_employee: dict = Depends(get_current_employee)
):
    """Stream agent trace events then the answer word-by-word using Server-Sent Events."""

    graph = get_graph()
    thread_id = request.thread_id or str(uuid.uuid4())
    employee_id = current_employee["employee_id"]

    async def event_generator():
        initial_state = {
            "question": request.question,
            "rewritten_question": "",
            "documents": [],
            "generation": "",
            "retrieval_attempts": 0,
            "relevance": "",
            "route": "",
            "retrieval_source": "",
            "chat_history": [
                {"role": msg.role, "content": msg.content}
                for msg in (request.chat_history or [])
            ],
            "employee_id": employee_id
        }

        config = {"configurable": {"thread_id": thread_id}}
        final_state = {}

        try:
            async for event in graph.astream(initial_state, config=config):
                for node_name, node_output in event.items():
                    final_state.update(node_output)
                    step = _build_trace_step(node_name, node_output, employee_id)
                    if step:
                        trace_data = {
                            "type": "trace",
                            "node": node_name,
                            "decision": step.decision,
                            "details": step.details
                        }
                        yield f"data: {json.dumps(trace_data)}\n\n"

            generation = final_state.get("generation", "")
            retrieval_source = final_state.get("retrieval_source", "")
            documents = final_state.get("documents", [])
            route = final_state.get("route", "")

            words = generation.split(" ")
            for i, word in enumerate(words):
                token = word if i == len(words) - 1 else word + " "
                yield f"data: {json.dumps({'type': 'token', 'value': token})}\n\n"
                await asyncio.sleep(0.03)

            # Run evaluation with a timeout so done is always sent promptly
            evaluation_data = None
            if route == "rag" and generation and retrieval_source:
                print(f"[Evaluation] Running for source={retrieval_source} route={route}")
                try:
                    evaluation_data = await asyncio.wait_for(
                        _run_and_save_evaluation(
                            request.question, generation, documents,
                            retrieval_source, employee_id, thread_id,
                        ),
                        timeout=15.0,
                    )
                    print(f"[Evaluation] Result: {evaluation_data}")
                except asyncio.TimeoutError:
                    print("[Evaluation] Timed out after 15s, skipping")

            yield f"data: {json.dumps({'type': 'done', 'thread_id': thread_id, 'retrieval_source': retrieval_source, 'sources': _parse_sources(generation), 'employee_id': employee_id, 'evaluation': evaluation_data})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
