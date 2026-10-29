"""Agent platform envelopes (Idea A) and automation run records (Idea B)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.app.schemas.models import ExecutionPlanOut, ReviewSourceOut


class AgentErrorBody(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None


class AgentEnvelope(BaseModel):
    success: bool
    agent: Optional[str] = None
    execution_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[AgentErrorBody] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRegistryItem(BaseModel):
    name: str
    kind: str  # interactive | automation
    enabled: bool
    description: str


class OrchestrateFilters(BaseModel):
    status: Optional[str] = None
    tag: Optional[str] = None
    file_type: Optional[str] = None


class OrchestrateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    filters: OrchestrateFilters = Field(default_factory=OrchestrateFilters)
    mode: str = Field(default="governed", pattern="^(governed|plan_only)$")
    submit_for_review: bool = True


class OrchestrateValidationOut(BaseModel):
    score: float
    supported: bool
    issues: List[str] = Field(default_factory=list)


class OrchestrateReviewOut(BaseModel):
    review_id: int
    status: str


class OrchestrateSourceOut(BaseModel):
    document: str
    page: int
    chunk_id: int
    score: float


class OrchestrateData(BaseModel):
    execution_id: str
    plan: ExecutionPlanOut
    evidence_count: int
    draft_answer: List[str]
    draft_answer_text: str
    validation: OrchestrateValidationOut
    review: Optional[OrchestrateReviewOut] = None
    sources: List[OrchestrateSourceOut] = Field(default_factory=list)
    steps_completed: List[str] = Field(default_factory=list)


class AutomationRunRequest(BaseModel):
    agents: List[str] = Field(
        default_factory=lambda: ["corpus_steward", "new_hire_autopilot", "search_quality"],
        description="Agent names to run; empty list runs all enabled automation agents.",
    )
    trigger: str = Field(default="manual", max_length=32)


class AutomationRunSummary(BaseModel):
    execution_id: str
    agent: str
    status: str
    message: str


class AutomationBatchResponse(BaseModel):
    batch_id: str
    runs: List[AutomationRunSummary]


class AgentRunRecord(BaseModel):
    execution_id: str
    agent_name: str
    status: str
    trigger: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None


class AgentInboxItem(BaseModel):
    execution_id: str
    agent_name: str
    status: str
    summary: str
    finished_at: Optional[datetime] = None
    report_path: Optional[str] = None


class AgentInboxResponse(BaseModel):
    items: List[AgentInboxItem] = Field(default_factory=list)


class ReviewTriageItem(BaseModel):
    review_id: int
    query: str
    confidence_score: float
    status: str


class ReviewTriageBatch(BaseModel):
    group_key: str
    label: str
    count: int
    items: List[ReviewTriageItem] = Field(default_factory=list)


class ReviewTriageResponse(BaseModel):
    total_pending: int
    batches: List[ReviewTriageBatch] = Field(default_factory=list)


class AutomationScheduleIn(BaseModel):
    enabled: bool = False
    day_pattern: str = Field(default="monday", pattern="^(daily|monday|weekdays)$")
    hour: int = Field(default=8, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    timezone: str = Field(default="UTC", max_length=64)
    agents: List[str] = Field(default_factory=list)


class AutomationScheduleOut(AutomationScheduleIn):
    last_run_at: Optional[str] = None


class AgentDashboardRunBrief(BaseModel):
    execution_id: str
    agent_name: str
    status: str
    finished_at: Optional[str] = None


class AgentDashboardOut(BaseModel):
    health: str  # green | yellow | red
    health_reasons: List[str] = Field(default_factory=list)
    health_actions: List[str] = Field(default_factory=list)
    pending_reviews: int
    zero_result_query_groups: int
    zero_result_recurring_groups: int = 0
    schedule_enabled: bool
    schedule_label: Optional[str] = None
    last_run_at: Optional[str] = None
    recent_runs: List[AgentDashboardRunBrief] = Field(default_factory=list)


class TriageBatchApproveRequest(BaseModel):
    min_confidence: float = Field(default=85.0, ge=50.0, le=100.0)
    max_count: int = Field(default=5, ge=1, le=20)
    group_key: Optional[str] = None


class TriageBatchApproveResult(BaseModel):
    approved_ids: List[int] = Field(default_factory=list)
    skipped: List[str] = Field(default_factory=list)
