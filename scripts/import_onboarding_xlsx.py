#!/usr/bin/env python3
"""Import Personalization KT onboarding Excel into NexusSearch."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.config import settings
from backend.app.db.connection import get_connection
from backend.app.services.onboarding_service import default_xlsx_path, import_xlsx


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_xlsx_path()
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        print(f"Expected default: {settings.onboarding_dir / settings.onboarding_xlsx_filename}")
        sys.exit(1)
    with get_connection() as conn:
        result = import_xlsx(conn, path)
    print(result.message)
    if result.search_document_id:
        print(f"Search corpus document id: {result.search_document_id}")


if __name__ == "__main__":
    main()
