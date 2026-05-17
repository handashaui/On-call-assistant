from fastapi.testclient import TestClient

from app.main import app


def ids(payload):
    return [item["id"] for item in payload["results"]]


def test_semantic_search_server_down_returns_backend_and_sre():
    with TestClient(app) as client:
        response = client.get("/v2/search", params={"q": "服务器挂了"})
    assert response.status_code == 200
    assert ids(response.json())[:2] == ["sop-001", "sop-004"]


def test_semantic_search_hacker_attack_returns_security():
    with TestClient(app) as client:
        response = client.get("/v2/search", params={"q": "黑客攻击"})
    assert response.status_code == 200
    assert ids(response.json())[0] == "sop-005"


def test_semantic_search_ml_model_problem_returns_ai():
    with TestClient(app) as client:
        response = client.get("/v2/search", params={"q": "机器学习模型出问题"})
    assert response.status_code == 200
    assert ids(response.json())[0] == "sop-008"


def test_semantic_search_hybrid_keeps_oom_backend_first():
    with TestClient(app) as client:
        response = client.get("/v2/search", params={"q": "OOM"})
    assert response.status_code == 200
    assert ids(response.json())[0] == "sop-001"


def test_semantic_search_hybrid_keeps_cdn_documents_high():
    with TestClient(app) as client:
        response = client.get("/v2/search", params={"q": "CDN"})
    assert response.status_code == 200
    result_ids = ids(response.json())
    assert result_ids[:2] == ["sop-003", "sop-010"]
