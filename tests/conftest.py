import os
import tempfile
from pathlib import Path

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Isolate SQLite before any test imports `backend.app.main` (module-level bootstrap)."""
    if os.environ.get("KNOWLEDGEPILOT_PYTEST_CONFIGURED") == "1":
        return
    base = Path(tempfile.mkdtemp(prefix="nexussearch_pytest_"))
    os.environ["KNOWLEDGEPILOT_DATA_DIR"] = str(base)
    onboarding = base / "onboarding"
    onboarding.mkdir(parents=True, exist_ok=True)
    os.environ["KNOWLEDGEPILOT_ONBOARDING_DIR"] = str(onboarding)
    os.environ["KNOWLEDGEPILOT_PYTEST_CONFIGURED"] = "1"


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    return Path(os.environ["KNOWLEDGEPILOT_DATA_DIR"])


@pytest.fixture(scope="session")
def api_app(test_data_dir: Path):
    from backend.app.main import app

    return app


@pytest.fixture
def client(api_app):
    from fastapi.testclient import TestClient

    with TestClient(api_app) as test_client:
        yield test_client
