"""Optional Bearer API key for agent / orchestration routes."""

from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException

from backend.app.config import settings


def require_agent_api_key(authorization: Optional[str] = Header(None)) -> None:
    expected = settings.api_key
    if not expected:
        return
    if not authorization or not authorization.strip().lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "AUTH_001",
                    "message": "Missing or invalid Authorization header (Bearer API key required)",
                },
            },
        )
    token = authorization.strip().split(" ", 1)[-1].strip()
    if token != expected:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "AUTH_001",
                    "message": "Invalid API key",
                },
            },
        )
