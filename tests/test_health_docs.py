import json


def test_health_endpoint_returns_status(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded")
    assert "services" in data
    assert "database" in data["services"]
    assert "redis" in data["services"]


def test_api_docs_structure(client):
    resp = client.get("/api/docs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "endpoints" in data
    # basic keys we advertise (match the detailed docs structure)
    expected_keys = ("GET /api/health", "GET /api/projects", "GET /api/project/<id>")
    for key in expected_keys:
        assert key in data["endpoints"]


def test_api_not_found_returns_json(client):
    resp = client.get("/api/this-does-not-exist")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data.get("error") is not None


