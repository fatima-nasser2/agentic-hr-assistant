import uuid
import json
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from api.models import FeedbackRequest, FeedbackResponse
from api.dependencies import get_current_employee
from src.database.query_engine import update_evaluation_feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])

FEEDBACK_FILE = "data/feedback.json"

def save_feedback(feedback: dict):
    os.makedirs("data", exist_ok=True)
    existing = []
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            existing = json.load(f)
    existing.append(feedback)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(existing, f, indent=2)

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    current_employee: dict = Depends(get_current_employee)
):
    """Submit thumbs up/down feedback for an answer."""
    feedback_id = str(uuid.uuid4())
    feedback = {
        "feedback_id": feedback_id,
        "employee_id": current_employee["employee_id"],
        "thread_id": request.thread_id,
        "question": request.question,
        "answer": request.answer,
        "rating": request.rating,
        "comment": request.comment,
        "eval_id": request.eval_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    save_feedback(feedback)

    # Link human rating to the evaluation record when available
    if request.eval_id:
        update_evaluation_feedback(request.eval_id, request.rating, request.comment)

    return FeedbackResponse(
        message=f"Feedback recorded — thank you!",
        feedback_id=feedback_id
    )