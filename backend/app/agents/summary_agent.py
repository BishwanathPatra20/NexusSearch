import re
from typing import List, Optional

from backend.app.schemas.models import SearchHit

_ACTION_LABEL = {
    "summarize": "Summary draft",
    "find_documents": "Document discovery draft",
    "compare_releases": "Release comparison draft",
    "list_related": "Related knowledge draft",
}


class SummaryAgent:
    """Extractive summary — no LLM, office-safe."""

    def execute(
        self,
        query: str,
        hits: List[SearchHit],
        intent: Optional[str] = None,
        action: Optional[str] = None,
    ) -> str:
        if not hits:
            return "No matching knowledge was found in the local repository for this question."

        label = _ACTION_LABEL.get(action or "", "Answer draft")
        header = f"{label} (intent={intent or 'general'}, action={action or 'summarize'})"
        lines = [header, f"Question: {query}", "", "Based on indexed sources:"]
        for i, hit in enumerate(hits[:5], start=1):
            snippet = re.sub(r"\s+", " ", hit.snippet).strip()
            cite = f"{hit.file_name} (p.{hit.page_number}, chunk {hit.chunk_id})"
            lines.append(f"{i}. {snippet}")
            lines.append(f"   Source: {cite}")
        if action == "list_related":
            related = []
            for hit in hits[:3]:
                for rel in hit.related_documents or []:
                    related.append(f"- {rel.title} ({rel.file_name})")
            if related:
                lines.extend(["", "Related documents (metadata):"] + related[:8])
        lines.append("")
        lines.append("Review and approve before treating this as official guidance.")
        return "\n".join(lines)
