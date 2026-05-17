from fastapi.testclient import TestClient

from app.main import app


def called_files(payload):
    return [item["arguments"]["fname"] for item in payload["tool_calls"]]


def test_agent_reads_database_sop_for_replication_lag():
    with TestClient(app) as client:
        response = client.post("/v3/chat", json={"message": "数据库主从延迟超过30秒怎么处理？"})
    assert response.status_code == 200
    payload = response.json()
    assert "sop-002.html" in called_files(payload)
    assert "主从" in payload["answer"]


def test_agent_reads_backend_sop_for_oom():
    with TestClient(app) as client:
        response = client.post("/v3/chat", json={"message": "服务 OOM 了怎么办？"})
    assert response.status_code == 200
    payload = response.json()
    assert "sop-001.html" in called_files(payload)
    assert "OOM" in payload["answer"] or "OutOfMemoryError" in payload["answer"]


def test_agent_combines_multiple_sops_for_p0():
    with TestClient(app) as client:
        response = client.post("/v3/chat", json={"message": "P0 故障的响应流程是什么？"})
    assert response.status_code == 200
    payload = response.json()
    assert len(called_files(payload)) >= 2
    assert "升级" in payload["answer"]


def test_agent_reads_security_sop_for_intrusion():
    with TestClient(app) as client:
        response = client.post("/v3/chat", json={"message": "怀疑有人入侵了系统"})
    assert response.status_code == 200
    payload = response.json()
    assert "sop-005.html" in called_files(payload)
    assert "安全" in payload["answer"] or "入侵" in payload["answer"]


def test_agent_reads_ai_sop_for_recommendation_quality_drop():
    with TestClient(app) as client:
        response = client.post("/v3/chat", json={"message": "推荐结果质量下降了"})
    assert response.status_code == 200
    payload = response.json()
    assert "sop-008.html" in called_files(payload)
    assert "模型" in payload["answer"] or "推荐" in payload["answer"]
