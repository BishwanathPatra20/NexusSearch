import sqlite3
from typing import List

from typing import Optional

from backend.app.schemas.models import SearchHit
from backend.app.schemas.search_filters import SearchFilters
from backend.app.services.search_service import search


class SearchAgent:
    def execute(
        self,
        conn: sqlite3.Connection,
        query: str,
        limit: int = 8,
        filters: Optional[SearchFilters] = None,
    ) -> List[SearchHit]:
        response = search(conn, query, limit=limit, filters=filters)
        return response.results
