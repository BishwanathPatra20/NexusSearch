from fastapi import APIRouter, Query

from backend.app.agents.planner_agent import PlannerAgent
from backend.app.db.connection import get_connection
from backend.app.schemas.models import AskRequest, AskResponse, ExecutionPlanOut
from backend.app.services.review_service import ask_and_queue

router = APIRouter(prefix="/ask", tags=["ask"])


@router.get("/plan", response_model=ExecutionPlanOut)
def preview_plan(q: str = Query(..., min_length=1, max_length=1000)) -> ExecutionPlanOut:
    """Structured planner output without running search or creating a review item."""
    return PlannerAgent().execute(q).to_api()


@router.post("", response_model=AskResponse)
def ask_question(body: AskRequest) -> AskResponse:
    with get_connection() as conn:
        return ask_and_queue(conn, body.query, submit_for_review=body.submit_for_review)
