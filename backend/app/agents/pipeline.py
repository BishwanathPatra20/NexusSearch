from dataclasses import dataclass
from typing import List, Optional

from backend.app.agents.planner_agent import PlannerAgent
from backend.app.schemas.search_filters import SearchFilters
from backend.app.agents.search_agent import SearchAgent
from backend.app.agents.summary_agent import SummaryAgent
from backend.app.agents.validator_agent import ValidationResult, ValidatorAgent
from backend.app.schemas.models import ExecutionPlanOut, SearchHit


@dataclass
class PipelineResult:
    plan: ExecutionPlanOut
    hits: List[SearchHit]
    draft_answer: str
    validation: ValidationResult


class KnowledgePipeline:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.search = SearchAgent()
        self.summary = SummaryAgent()
        self.validator = ValidatorAgent()

    def run(
        self,
        conn,
        query: str,
        filters: Optional[SearchFilters] = None,
    ) -> PipelineResult:
        execution_plan = self.planner.execute(query)
        plan_out = execution_plan.to_api()
        hits = self.search.execute(conn, query, filters=filters)
        draft = self.summary.execute(
            query,
            hits,
            intent=plan_out.structured.intent,
            action=plan_out.structured.action,
        )
        validation = self.validator.execute(draft, hits)
        return PipelineResult(
            plan=plan_out,
            hits=hits,
            draft_answer=draft,
            validation=validation,
        )
