import re
from dataclasses import dataclass, field
from typing import List

from backend.app.schemas.models import SearchHit


@dataclass
class ValidationResult:
    confidence_score: float
    passed: bool
    notes: List[str] = field(default_factory=list)


class ValidatorAgent:
    """Checks that draft lines are supported by retrieved chunks."""

    def execute(self, draft_answer: str, hits: List[SearchHit]) -> ValidationResult:
        if not hits:
            return ValidationResult(
                confidence_score=0.0,
                passed=False,
                notes=["No sources retrieved."],
            )

        corpus = " ".join(
            re.sub(r"\s+", " ", (h.snippet or "").lower()) for h in hits
        )
        corpus_words = set(re.findall(r"[a-z0-9]{3,}", corpus))

        bullet_lines = [
            ln.strip()
            for ln in draft_answer.splitlines()
            if ln.strip() and not ln.strip().startswith("Source:")
        ]
        content_lines = [
            ln
            for ln in bullet_lines
            if not ln.lower().startswith("answer draft")
            and not ln.lower().startswith("based on")
            and not ln.lower().startswith("review and approve")
        ]

        supported = 0
        notes: List[str] = []
        for line in content_lines[:8]:
            words = set(re.findall(r"[a-z0-9]{3,}", line.lower()))
            if len(words) < 3:
                continue
            overlap = len(words & corpus_words) / max(len(words), 1)
            if overlap >= 0.35:
                supported += 1
            else:
                notes.append(f"Low source overlap for line: {line[:80]}…")

        avg_hit_score = sum(h.score for h in hits) / len(hits)
        coverage = supported / max(len(content_lines), 1)
        confidence = min(100.0, (avg_hit_score * 0.6) + (coverage * 40.0))
        passed = confidence >= 55.0 and supported >= 1

        if avg_hit_score >= 70:
            notes.append("+ Strong retrieval scores")
        if any(h.document_status.value == "active" for h in hits):
            notes.append("+ Active documents in results")

        return ValidationResult(
            confidence_score=round(confidence, 1),
            passed=passed,
            notes=notes,
        )
