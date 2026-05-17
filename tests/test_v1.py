from fastapi.testclient import TestClient

from app.main import app


def ids(payload):
    return [item["id"] for item in payload["results"]]


def test_keyword_search_oom_returns_backend_sop():
    with TestClient(app) as client:
        response = client.get("/v1/search", params={"q": "OOM"})
    assert response.status_code == 200
    assert ids(response.json())[0] == "sop-001"


def test_keyword_search_fault_returns_multiple_documents():
    with TestClient(app) as client:
        response = client.get("/v1/search", params={"q": "故障"})
    assert response.status_code == 200
    assert len(response.json()["results"]) >= 5


def test_keyword_search_ignores_script_tags():
    with TestClient(app) as client:
        response = client.get("/v1/search", params={"q": "replication"})
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_keyword_search_cdn_returns_frontend_and_network_sops():
    with TestClient(app) as client:
        response = client.get("/v1/search", params={"q": "CDN"})
    assert response.status_code == 200
    result_ids = ids(response.json())
    assert "sop-003" in result_ids
    assert "sop-010" in result_ids


def test_keyword_search_decodes_html_entities():
    with TestClient(app) as client:
        response = client.get("/v1/search", params={"q": "&"})
    assert response.status_code == 200
    result_ids = ids(response.json())
    assert "sop-003" in result_ids
    assert "sop-010" in result_ids
