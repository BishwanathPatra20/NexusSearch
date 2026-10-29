"""Confluence REST client (Cloud basic auth or Server/DC Bearer PAT)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import httpx

from backend.app.config import settings


class ConfluenceConfigError(Exception):
    pass


class ConfluenceApiError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _normalize_base_url(raw: str) -> str:
    base = raw.strip().rstrip("/")
    if not base.startswith("http"):
        raise ConfluenceConfigError("CONFLUENCE_BASE_URL must start with https://")
    if "atlassian.net" in base.lower() and not base.endswith("/wiki"):
        base = f"{base}/wiki"
    return base


def resolve_auth_mode() -> str:
    mode = (settings.confluence_auth_mode or "auto").strip().lower()
    if mode in ("basic", "bearer"):
        return mode
    if settings.confluence_base_url and "atlassian.net" in settings.confluence_base_url.lower():
        return "basic"
    return "bearer"


def confluence_configured() -> bool:
    if not settings.confluence_enabled or not settings.confluence_base_url or not settings.confluence_api_token:
        return False
    if resolve_auth_mode() == "basic" and not settings.confluence_email:
        return False
    return True


class ConfluenceClient:
    def __init__(self) -> None:
        if not settings.confluence_enabled:
            raise ConfluenceConfigError(
                "Confluence API is disabled. Set KNOWLEDGEPILOT_CONFLUENCE_ENABLED=true in .env"
            )
        if not settings.confluence_base_url or not settings.confluence_api_token:
            raise ConfluenceConfigError(
                "Set KNOWLEDGEPILOT_CONFLUENCE_BASE_URL and CONFLUENCE_API_TOKEN in .env"
            )
        mode = resolve_auth_mode()
        if mode == "basic" and not settings.confluence_email:
            raise ConfluenceConfigError(
                "Basic auth requires KNOWLEDGEPILOT_CONFLUENCE_EMAIL (or set CONFLUENCE_AUTH_MODE=bearer)"
            )
        self.base_url = _normalize_base_url(settings.confluence_base_url)
        self._auth_mode = mode
        self._token = settings.confluence_api_token.strip()
        self._email = (settings.confluence_email or "").strip()

    def _request_auth(self, mode: str) -> Tuple[Optional[Tuple[str, str]], Dict[str, str]]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if mode == "bearer":
            headers["Authorization"] = f"Bearer {self._token}"
            return None, headers
        return (self._email, self._token), headers

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return urljoin(self.base_url + "/", path.lstrip("/"))

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = self._url(path)
        modes_to_try = [self._auth_mode]
        if self._auth_mode == "auto":
            modes_to_try = ["bearer", "basic"]
        elif self._auth_mode == "basic":
            modes_to_try = ["basic", "bearer"]

        last_error: Optional[ConfluenceApiError] = None
        for mode in modes_to_try:
            auth, headers = self._request_auth(mode)
            try:
                with httpx.Client(timeout=60.0, verify=settings.confluence_verify_ssl) as client:
                    response = client.get(url, params=params or {}, auth=auth, headers=headers)
            except httpx.RequestError as exc:
                raise ConfluenceApiError(f"Network error calling Confluence: {exc}") from exc

            if response.status_code == 401:
                last_error = ConfluenceApiError("Unauthorized — check PAT/token or auth mode", 401)
                continue
            if response.status_code == 403 and "Basic Authentication has been disabled" in response.text:
                last_error = ConfluenceApiError(
                    "Basic auth disabled on this server — use CONFLUENCE_AUTH_MODE=bearer with a PAT",
                    403,
                )
                continue
            if response.status_code >= 400:
                raise ConfluenceApiError(
                    f"Confluence HTTP {response.status_code}: {response.text[:400]}",
                    response.status_code,
                )
            return response.json()

        if last_error:
            raise last_error
        raise ConfluenceApiError("Confluence request failed", None)

    def ping(self) -> Dict[str, Any]:
        return self._get("/rest/api/user/current")

    def get_space(self, space_key: str) -> Dict[str, Any]:
        key = space_key.strip().upper()
        return self._get(f"/rest/api/space/{key}")

    def get_page(self, page_id: str) -> Dict[str, Any]:
        return self._get(
            f"/rest/api/content/{page_id.strip()}",
            params={"expand": "body.storage,version,space,_links"},
        )

    def list_spaces(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Paginate space list (corporate instances often have hundreds of spaces)."""
        collected: List[Dict[str, Any]] = []
        page_size = min(100, limit)
        start = 0
        while len(collected) < limit:
            data = self._get(
                "/rest/api/space",
                params={"limit": page_size, "start": start},
            )
            batch = list(data.get("results") or [])
            if not batch:
                break
            collected.extend(batch)
            if len(batch) < page_size:
                break
            start += page_size
        return collected[:limit]

    def search_cql(self, cql: str, limit: int = 10, start: int = 0) -> Dict[str, Any]:
        return self._get(
            "/rest/api/content/search",
            params={
                "cql": cql,
                "limit": min(limit, 50),
                "start": start,
                "expand": "body.storage,space,_links",
            },
        )

    def list_pages(
        self,
        space_key: str,
        limit: int = 25,
        start: int = 0,
    ) -> Dict[str, Any]:
        return self._get(
            "/rest/api/content",
            params={
                "spaceKey": space_key,
                "type": "page",
                "limit": limit,
                "start": start,
                "expand": "body.storage,version,_links",
            },
        )

    def list_child_pages(
        self,
        parent_id: str,
        limit: int = 50,
        start: int = 0,
    ) -> Dict[str, Any]:
        return self._get(
            f"/rest/api/content/{parent_id.strip()}/child/page",
            params={
                "limit": limit,
                "start": start,
                "expand": "body.storage,version,space,_links",
            },
        )

    def collect_descendant_page_ids(
        self,
        root_page_id: str,
        max_pages: int = 100,
        include_root: bool = True,
    ) -> List[str]:
        """Breadth-first collection of child page IDs (direct descendants only per level)."""
        root = root_page_id.strip()
        seen: set[str] = set()
        ordered: List[str] = []
        if include_root:
            seen.add(root)
            ordered.append(root)
        queue: List[str] = [root]
        while queue and len(ordered) < max_pages:
            parent = queue.pop(0)
            start = 0
            page_size = min(50, max_pages - len(ordered))
            while len(ordered) < max_pages:
                data = self.list_child_pages(parent, limit=page_size, start=start)
                batch = list(data.get("results") or [])
                if not batch:
                    break
                for page in batch:
                    pid = str(page.get("id", ""))
                    if not pid or pid in seen:
                        continue
                    seen.add(pid)
                    ordered.append(pid)
                    queue.append(pid)
                    if len(ordered) >= max_pages:
                        break
                if len(batch) < page_size:
                    break
                start += len(batch)
        return ordered[:max_pages]

    @staticmethod
    def page_web_url(page: Dict[str, Any]) -> Optional[str]:
        links = page.get("_links") or {}
        webui = links.get("webui")
        base = links.get("base") or ""
        if webui and base:
            return urljoin(base, webui)
        if webui and webui.startswith("http"):
            return webui
        return None

    @staticmethod
    def page_storage_html(page: Dict[str, Any]) -> str:
        body = page.get("body") or {}
        storage = body.get("storage") or {}
        return str(storage.get("value") or "")
