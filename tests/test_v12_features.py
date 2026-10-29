def test_automation_dashboard(client):
    r = client.get("/api/v1/automations/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["health"] in ("green", "yellow", "red")


def test_config_status(client):
    r = client.get("/api/v1/config/status")
    assert r.status_code == 200
    assert "watch_enabled" in r.json()


def test_synonym_proposals_empty(client):
    r = client.get("/api/v1/synonyms/proposals")
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_audit_export(client):
    r = client.get("/api/v1/analytics/export/audit-pack.csv")
    assert r.status_code == 200
    assert "NexusSearch audit export" in r.text


def test_schedule_timezone(client):
    r = client.put(
        "/api/v1/automations/schedule",
        json={
            "enabled": False,
            "day_pattern": "monday",
            "hour": 9,
            "minute": 0,
            "timezone": "Asia/Kolkata",
            "agents": ["corpus_steward"],
        },
    )
    assert r.status_code == 200
    assert r.json()["timezone"] == "Asia/Kolkata"
