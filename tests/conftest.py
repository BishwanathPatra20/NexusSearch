import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    data = tmp_path_factory.mktemp("nexussearch_data")
    os.environ["KNOWLEDGEPILOT_DATA_DIR"] = str(data)
    # Empty onboarding dir so startup does not auto-import the repo workbook into test DB.
    onboarding = data / "onboarding"
    onboarding.mkdir(parents=True, exist_ok=True)
    os.environ["KNOWLEDGEPILOT_ONBOARDING_DIR"] = str(onboarding)
    return data


@pytest.fixture(scope="session")
def api_app(test_data_dir: Path):
    from backend.app.main import app

    return app


@pytest.fixture
def client(api_app):
    from fastapi.testclient import TestClient

    with TestClient(api_app) as test_client:
        yield test_client
