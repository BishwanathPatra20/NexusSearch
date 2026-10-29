import json
import os
from typing import Any, Dict, List, Optional

import httpx

API_ROOT = os.environ.get("KNOWLEDGEPILOT_API_ROOT", "http://127.0.0.1:8000").rstrip("/")
API_BASE = os.environ.get("KNOWLEDGEPILOT_API_URL", f"{API_ROOT}/api/v1")
TIMEOUT = 120.0
_API_KEY = os.environ.get("KNOWLEDGEPILOT_API_KEY", "").strip()


def _agent_headers() -> Dict[str, str]:
    if not _API_KEY:
        return {}
    return {"Authorization": f"Bearer {_API_KEY}"}


def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE, timeout=TIMEOUT)


def _agent_client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE, timeout=TIMEOUT, headers=_agent_headers())


def health() -> Dict[str, Any]:
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(f"{API_ROOT}/health")
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} from {API_ROOT}/health: {r.text[:500]}")
        data = r.json()
        if data.get("service") not in (None, "nexussearch"):
            raise RuntimeError(
                f"Wrong API on {API_ROOT} (service={data.get('service')}). "
                "Stop the other process on port 8000 and start NexusSearch ./scripts/start-api.sh"
            )
        return data


def confluence_status() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/confluence/status")
        r.raise_for_status()
        return r.json()


def confluence_spaces(limit: int = 500) -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get("/confluence/spaces", params={"limit": limit})
        r.raise_for_status()
        return r.json()


def confluence_validate_space(space_key: str) -> Dict[str, Any]:
    key = space_key.strip().upper()
    with _client() as client:
        r = client.get(f"/confluence/space/{key}")
        r.raise_for_status()
        return r.json()


def confluence_sync_page(
    page_id: str,
    tags: Optional[List[str]] = None,
    replace_existing: bool = True,
) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/confluence/sync-page",
            json={
                "page_id": str(page_id).strip(),
                "tags": tags or [],
                "replace_existing": replace_existing,
            },
        )
        r.raise_for_status()
        return r.json()


def confluence_sync_pages(
    page_ids: List[str],
    tags: Optional[List[str]] = None,
    replace_existing: bool = True,
) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/confluence/sync-pages",
            json={
                "page_ids": [str(p).strip() for p in page_ids if str(p).strip()],
                "tags": tags or [],
                "replace_existing": replace_existing,
            },
        )
        r.raise_for_status()
        return r.json()


def confluence_sync_descendants(
    parent_page_id: str,
    max_pages: int = 50,
    tags: Optional[List[str]] = None,
    include_parent: bool = True,
) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/confluence/sync-descendants",
            json={
                "parent_page_id": str(parent_page_id).strip(),
                "max_pages": max_pages,
                "include_parent": include_parent,
                "tags": tags or [],
                "replace_existing": True,
            },
        )
        r.raise_for_status()
        return r.json()


def confluence_sync_job(
    *,
    space_key: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    limit: int = 100,
    max_pages: int = 100,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "limit": limit,
        "max_pages": max_pages,
        "tags": tags or [],
        "replace_existing": True,
    }
    if space_key:
        payload["space_key"] = space_key
    if parent_page_id:
        payload["parent_page_id"] = parent_page_id
    with _client() as client:
        r = client.post("/confluence/sync-job", json=payload)
        r.raise_for_status()
        return r.json()


def confluence_stats() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/confluence/stats")
        r.raise_for_status()
        return r.json()


def confluence_sync(space_key: str, limit: int = 25, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/confluence/sync",
            json={
                "space_key": space_key,
                "limit": limit,
                "tags": tags or [],
                "replace_existing": True,
            },
        )
        r.raise_for_status()
        return r.json()


def upload_file(
    file_name: str,
    file_bytes: bytes,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    data = {"tags_json": json.dumps(tags or [])}
    if title:
        data["title"] = title
    files = {"file": (file_name, file_bytes)}
    with _client() as client:
        r = client.post("/documents/upload", data=data, files=files)
        r.raise_for_status()
        return r.json()


def ingest_folder(folder_path: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/documents/ingest-folder",
            json={
                "folder_path": folder_path,
                "tags": tags or [],
                "recursive": True,
                "async_job": True,
            },
        )
        r.raise_for_status()
        return r.json()


def get_job(job_id: int) -> Dict[str, Any]:
    with _client() as client:
        r = client.get(f"/jobs/{job_id}")
        r.raise_for_status()
        return r.json()


def list_jobs(limit: int = 15) -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get("/jobs", params={"limit": limit})
        r.raise_for_status()
        return r.json()


def list_documents(source_type: Optional[str] = None) -> List[Dict[str, Any]]:
    params = {"source_type": source_type} if source_type else None
    with _client() as client:
        r = client.get("/documents", params=params)
        r.raise_for_status()
        return r.json()


def get_document(document_id: int) -> Dict[str, Any]:
    with _client() as client:
        r = client.get(f"/documents/{document_id}")
        r.raise_for_status()
        return r.json()


def patch_document(document_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    with _client() as client:
        r = client.patch(f"/documents/{document_id}", json=payload)
        r.raise_for_status()
        return r.json()


def get_chunks(document_id: int) -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get(f"/documents/{document_id}/chunks")
        r.raise_for_status()
        return r.json()


def search(
    query: str,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    file_type: Optional[str] = None,
    version_label: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {"q": query}
    if status:
        params["status"] = status
    if tag:
        params["tag"] = tag
    if file_type:
        params["file_type"] = file_type
    if version_label:
        params["version_label"] = version_label
    with _client() as client:
        r = client.get("/search", params=params)
        r.raise_for_status()
        return r.json()


def record_search_click(
    query: str,
    chunk_id: int,
    click_position: int,
    search_id: Optional[int] = None,
) -> None:
    with _client() as client:
        r = client.post(
            "/search/click",
            json={
                "query": query,
                "chunk_id": chunk_id,
                "click_position": click_position,
                "search_id": search_id,
            },
        )
        r.raise_for_status()


def governance_metrics() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/analytics/governance")
        r.raise_for_status()
        return r.json()


def analytics_summary() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/analytics/summary")
        r.raise_for_status()
        return r.json()


def preview_plan(query: str) -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/ask/plan", params={"q": query})
        r.raise_for_status()
        return r.json()


def ask(query: str, submit_for_review: bool = True) -> Dict[str, Any]:
    with _client() as client:
        r = client.post("/ask", json={"query": query, "submit_for_review": submit_for_review})
        r.raise_for_status()
        return r.json()


def list_reviews(status: Optional[str] = None) -> List[Dict[str, Any]]:
    params = {"status": status} if status else None
    with _client() as client:
        r = client.get("/reviews", params=params)
        r.raise_for_status()
        return r.json()


def get_review(review_id: int) -> Dict[str, Any]:
    with _client() as client:
        r = client.get(f"/reviews/{review_id}")
        r.raise_for_status()
        return r.json()


def review_audit(review_id: int) -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get(f"/reviews/{review_id}/audit")
        r.raise_for_status()
        return r.json()


def approve_review(review_id: int, comment: Optional[str] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(f"/reviews/{review_id}/approve", json={"comment": comment})
        r.raise_for_status()
        return r.json()


def reject_review(review_id: int, comment: Optional[str] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(f"/reviews/{review_id}/reject", json={"comment": comment})
        r.raise_for_status()
        return r.json()


def edit_review(review_id: int, final_answer: str, comment: Optional[str] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            f"/reviews/{review_id}/edit",
            json={"final_answer": final_answer, "comment": comment},
        )
        r.raise_for_status()
        return r.json()


def list_lineage_index() -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get("/lineage")
        r.raise_for_status()
        return r.json()


def get_lineage(review_item_id: int) -> Dict[str, Any]:
    with _client() as client:
        r = client.get(f"/lineage/{review_item_id}")
        r.raise_for_status()
        return r.json()


def get_onboarding_meta() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/onboarding/meta")
        r.raise_for_status()
        return r.json()


def get_onboarding_items(
    q: Optional[str] = None,
    category: Optional[str] = None,
    day: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if q:
        params["q"] = q
    if category:
        params["category"] = category
    if day:
        params["day"] = day
    with _client() as client:
        r = client.get("/onboarding/items", params=params)
        r.raise_for_status()
        return r.json()


def import_onboarding_file(file_name: str, file_bytes: bytes) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/onboarding/import-file",
            files={"file": (file_name, file_bytes)},
        )
        r.raise_for_status()
        return r.json()


def import_onboarding_default() -> Dict[str, Any]:
    with _client() as client:
        r = client.post("/onboarding/import-default")
        r.raise_for_status()
        return r.json()


def onboarding_link_health() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/onboarding/link-health")
        r.raise_for_status()
        return r.json()


def onboarding_sync_confluence(tags: Optional[List[str]] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/onboarding/sync-confluence",
            json={"tags": tags or ["confluence", "onboarding"]},
        )
        r.raise_for_status()
        return r.json()


def get_onboarding_suggested_asks(limit: int = 12) -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/onboarding/suggested-asks", params={"limit": limit})
        r.raise_for_status()
        return r.json()


def agents_registry() -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get("/agents")
        r.raise_for_status()
        return r.json()


def orchestrate(
    query: str,
    mode: str = "governed",
    submit_for_review: bool = True,
) -> Dict[str, Any]:
    with _agent_client() as client:
        r = client.post(
            "/orchestrate",
            json={
                "query": query,
                "mode": mode,
                "submit_for_review": submit_for_review,
                "filters": {},
            },
        )
        r.raise_for_status()
        return r.json()


def run_automations(agent_names: Optional[List[str]] = None) -> Dict[str, Any]:
    with _agent_client() as client:
        r = client.post(
            "/automations/run",
            json={"agents": agent_names or [], "trigger": "manual"},
        )
        r.raise_for_status()
        body = r.json()
        return body.get("data") or body


def agents_inbox() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/automations/inbox")
        r.raise_for_status()
        return r.json()


def get_automation_schedule() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/automations/schedule")
        r.raise_for_status()
        return r.json()


def save_automation_schedule(
    enabled: bool,
    day_pattern: str,
    hour: int,
    minute: int,
    agents: List[str],
    timezone: str = "UTC",
) -> Dict[str, Any]:
    with _agent_client() as client:
        r = client.put(
            "/automations/schedule",
            json={
                "enabled": enabled,
                "day_pattern": day_pattern,
                "hour": hour,
                "minute": minute,
                "timezone": timezone,
                "agents": agents,
            },
        )
        r.raise_for_status()
        return r.json()


def agent_dashboard() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/automations/dashboard")
        r.raise_for_status()
        return r.json()


def config_status() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/config/status")
        r.raise_for_status()
        return r.json()


def synonym_proposals() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/synonyms/proposals")
        r.raise_for_status()
        return r.json()


def approve_synonym_proposal(proposal_id: int) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(f"/synonyms/proposals/{proposal_id}/approve")
        r.raise_for_status()
        return r.json()


def dismiss_synonym_proposal(proposal_id: int) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(f"/synonyms/proposals/{proposal_id}/dismiss")
        r.raise_for_status()
        return r.json()


def triage_batch_approve(
    min_confidence: float = 85.0,
    max_count: int = 5,
    group_key: Optional[str] = None,
) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/reviews/triage/batch-approve",
            json={
                "min_confidence": min_confidence,
                "max_count": max_count,
                "group_key": group_key,
            },
        )
        r.raise_for_status()
        return r.json()


def fetch_audit_pack_csv() -> str:
    with _client() as client:
        r = client.get("/analytics/export/audit-pack.csv")
        r.raise_for_status()
        return r.text


def review_triage() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/reviews/triage")
        r.raise_for_status()
        return r.json()


def list_agent_runs(limit: int = 30) -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get("/automations/runs", params={"limit": limit})
        r.raise_for_status()
        return r.json()


def list_approved_knowledge() -> List[Dict[str, Any]]:
    with _client() as client:
        r = client.get("/reviews/approved")
        r.raise_for_status()
        return r.json()


def rag_status() -> Dict[str, Any]:
    with _client() as client:
        r = client.get("/rag/status")
        r.raise_for_status()
        return r.json()


def rag_chat(message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    with _client() as client:
        r = client.post(
            "/rag/chat",
            json={"message": message, "history": history or []},
        )
        r.raise_for_status()
        return r.json()
