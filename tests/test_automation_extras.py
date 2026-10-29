def test_review_triage_empty(client):
    r = client.get("/api/v1/reviews/triage")
    assert r.status_code == 200
    data = r.json()
    assert data["total_pending"] == 0
    assert data["batches"] == []


def test_automation_schedule_roundtrip(client):
    r = client.get("/api/v1/automations/schedule")
    assert r.status_code == 200
    r2 = client.put(
        "/api/v1/automations/schedule",
        json={
            "enabled": True,
            "day_pattern": "monday",
            "hour": 8,
            "minute": 30,
            "agents": ["corpus_steward", "ingest_watcher"],
        },
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["enabled"] is True
    assert body["hour"] == 8
    assert "ingest_watcher" in body["agents"]


def test_ingest_watcher_agent(client):
    r = client.post(
        "/api/v1/automations/run",
        json={"agents": ["ingest_watcher"], "trigger": "manual"},
    )
    assert r.status_code == 200
    runs = r.json()["data"]["runs"]
    assert runs[0]["status"] == "completed"
