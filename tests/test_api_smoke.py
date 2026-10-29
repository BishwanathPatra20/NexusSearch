def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "nexussearch"
    assert body["version"] == "1.1.0"


def test_analytics_summary_empty(client):
    r = client.get("/api/v1/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert "total_searches" in data
    assert "search_volume_by_day" in data
    assert data["total_searches"] == 0


def test_onboarding_meta_empty(client):
    r = client.get("/api/v1/onboarding/meta")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0


def test_onboarding_link_health_empty(client):
    r = client.get("/api/v1/onboarding/link-health")
    assert r.status_code == 200
    data = r.json()
    assert data["total_with_url"] == 0
