import re
from dataclasses import dataclass, field
from typing import List, Tuple

from backend.app.config import settings
from backend.app.schemas.models import ExecutionPlanOut, PlanStepOut, StructuredPlanOut

_COMPARE = re.compile(r"\b(compare|difference|diff|vs\.?|changed|what.?s new)\b", re.I)
_RELEASE = re.compile(r"\brelease\b|\bv\d", re.I)
_ONBOARD = re.compile(r"\b(onboard|joiner|new hire|access|provision|databricks|workspace)\b", re.I)
_DEPLOY = re.compile(r"\b(deploy|rollout|release|production|rollback|revert)\b", re.I)
_FIND = re.compile(r"\b(where|which doc|locate|find document)\b", re.I)
_RELATED = re.compile(r"\b(related|linked|associated)\b", re.I)
_SUMMARIZE = re.compile(r"\b(how do|how to|steps|summarize|explain|list)\b", re.I)


@dataclass
class PlanStep:
    name: str
    detail: str


@dataclass
class ExecutionPlan:
    query: str
    structured: StructuredPlanOut
    steps: List[PlanStep] = field(default_factory=list)

    def to_api(self) -> ExecutionPlanOut:
        return ExecutionPlanOut(
            query=self.query,
            structured=self.structured,
            steps=[PlanStepOut(name=s.name, detail=s.detail) for s in self.steps],
        )


class PlannerAgent:
    """Rule-based planner — structured JSON for routing (no LLM)."""

    def execute(self, query: str) -> ExecutionPlan:
        q = query.strip()
        intent, action, notes = self._classify(q)
        structured = StructuredPlanOut(
            intent=intent,
            action=action,
            requires_sources=True,
            requires_review=True,
            confidence_threshold=settings.planner_confidence_threshold,
            routing_notes=notes,
        )
        steps = self._steps_for_action(action)
        return ExecutionPlan(query=q, structured=structured, steps=steps)

    def _classify(self, q: str) -> Tuple[str, str, List[str]]:
        notes: List[str] = []
        if _COMPARE.search(q) or (_RELEASE.search(q) and "release" in q.lower()):
            notes.append("Detected compare/release language")
            return "release_compare", "compare_releases", notes
        if _RELATED.search(q):
            notes.append("Detected related-document intent")
            return "discovery", "list_related", notes
        if _FIND.search(q):
            notes.append("Detected document discovery intent")
            return "discovery", "find_documents", notes
        if _ONBOARD.search(q):
            notes.append("Detected onboarding/access vocabulary")
            return "onboarding", "summarize", notes
        if _DEPLOY.search(q):
            notes.append("Detected deployment/operations vocabulary")
            return "deployment", "summarize", notes
        if _SUMMARIZE.search(q):
            notes.append("Detected procedural question pattern")
            return "general", "summarize", notes
        notes.append("Default routing")
        return "general", "summarize", notes

    def _steps_for_action(self, action: str) -> List[PlanStep]:
        base = [
            PlanStep("search", "Retrieve ranked chunks (FTS5 + synonyms + filters)"),
            PlanStep("summarize", "Build extractive draft from top sources"),
            PlanStep("validate", "Score draft against cited chunks"),
            PlanStep("review", "Enqueue for human approval"),
        ]
        if action == "find_documents":
            base[1] = PlanStep("rank", "Prioritize document-level matches and citations")
        elif action == "compare_releases":
            base[1] = PlanStep("summarize", "Extract comparative bullets across release sources")
        elif action == "list_related":
            base.insert(1, PlanStep("graph", "Resolve related_document links from metadata"))
        return base
