def test_agents_registry(client):
    r = client.get("/api/v1/agents")
    assert r.status_code == 200
    data = r.json()
    names = {a["name"] for a in data}
    assert "orchestrate" in names
    assert "corpus_steward" in names


def test_orchestrate_plan_only(client):
    r = client.post(
        "/api/v1/orchestrate",
        json={"query": "Databricks access", "mode": "plan_only", "submit_for_review": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["plan"]["structured"]["intent"]
    assert body["data"]["evidence_count"] == 0


def test_automations_run_corpus_steward(client):
    r = client.post(
        "/api/v1/automations/run",
        json={"agents": ["corpus_steward"], "trigger": "test"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    runs = body["data"]["runs"]
    assert runs[0]["agent"] == "corpus_steward"
    assert runs[0]["status"] == "completed"


def test_automations_inbox(client):
    client.post(
        "/api/v1/automations/run",
        json={"agents": ["search_quality"], "trigger": "test"},
    )
    r = client.get("/api/v1/automations/inbox")
    assert r.status_code == 200
    assert "items" in r.json()
