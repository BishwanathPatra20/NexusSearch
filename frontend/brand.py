"""Single brand mark: frontend/static/system-search.webp"""

import base64
from pathlib import Path

ICON_PATH = Path(__file__).resolve().parent / "static" / "system-search.webp"


def brand_icon_data_uri() -> str:
    if not ICON_PATH.is_file():
        return ""
    encoded = base64.b64encode(ICON_PATH.read_bytes()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"
