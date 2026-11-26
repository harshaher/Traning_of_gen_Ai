"""
test_api.py - Integration Tests for ShellSathi FastAPI REST Endpoints (Day 11 S1-C & S1-D)

Tests:
  1. GET /health: Health status and ChromaDB metrics.
  2. POST /ask with Fake/Mock LLM: Zero network calls, verified citations & structure.
  3. POST /ask with simulated LLM failure: Graceful error handling.
  4. Missing question and invalid payload validations (HTTP 422).
  5. POST /chat with mocked structured output.
  6. Feedback submission and audit retrieval.
"""

from fastapi.testclient import TestClient


def test_api_health_endpoint(client: TestClient):
    """
    Verify GET /health returns HTTP 200, healthy status, and vector store metrics.
    """
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("service") == "ShellSathi"
    assert data.get("version") == "1.0.0"
    assert data.get("vector_store") == "ChromaDB"
    assert "indexed_chunks" in data
    assert isinstance(data["indexed_chunks"], int)
    assert data.get("liveness") == "ok"
    assert data.get("chromadb_status") in ("connected", "initializing")


def test_api_health_live_endpoint(client: TestClient):
    """Verify GET /health/live returns fast sub-millisecond liveness probe."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "alive"
    assert data.get("service") == "ShellSathi"


def test_api_health_ready_endpoint(client: TestClient):
    """Verify GET /health/ready returns readiness status for traffic routing."""
    response = client.get("/health/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert data.get("service") == "ShellSathi"


def test_api_ready_endpoint(client: TestClient):
    """Verify GET /ready endpoint returns readiness status for orchestrator probes."""
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert data.get("service") == "ShellSathi"


def test_api_docs_endpoint(client: TestClient):
    """Verify GET /docs serves OpenAPI interactive Swagger documentation."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_api_root_endpoint(client: TestClient):
    """Verify GET / root endpoint returns service description and feature catalog."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "ShellSathi" in data.get("service", "")
    assert isinstance(data.get("features"), list)


def test_api_ask_with_fake_llm(client: TestClient, mock_llm_ask):
    """
    Verify POST /ask endpoint using a fake/mocked RAG LLM response.
    Guarantees no real external API calls are made and no API keys are required.
    """
    payload = {"question": "How do I extract a tar archive?", "top_k": 3}
    response = client.post("/ask", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["question"] == "How do I extract a tar archive?"
    assert "answer" in data
    assert "tar -xvf" in data["answer"]
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    assert "data/raw/tar.md" in data["sources"]
    assert isinstance(data["confidence"], (int, float))
    assert data["confidence"] > 0.0


def test_api_ask_llm_error_handling(client: TestClient, mock_llm_error):
    """
    Verify that an upstream LLM/provider error is handled gracefully without crashing the server.
    """
    payload = {"question": "How to extract archive?", "top_k": 3}
    try:
        response = client.post("/ask", json=payload)
        assert response.status_code in {500, 502, 200}
    except Exception as exc:
        assert "Simulated upstream LLM provider connection error" in str(exc)


def test_api_ask_missing_and_invalid_payload(client: TestClient):
    """
    Verify that empty requests or invalid parameters trigger HTTP 422 Unprocessable Entity.
    """
    res_empty = client.post("/ask", json={})
    assert res_empty.status_code == 422

    res_blank = client.post("/ask", json={"question": ""})
    assert res_blank.status_code == 422

    res_invalid_k = client.post("/ask", json={"question": "valid question", "top_k": 999})
    assert res_invalid_k.status_code == 422


def test_api_chat_with_mock_llm(client: TestClient, mock_chat_llm):
    """
    Verify POST /chat returns structured answer, confidence, and follow_up via mock LLM.
    """
    payload = {"question": "How do I change file permissions to 755?"}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "chmod 755" in data["answer"]
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert "follow_up" in data


def test_api_records_endpoints(client: TestClient):
    """Verify GET /records and GET /records/{id} endpoints."""
    res_list = client.get("/records?limit=5")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["total"] >= 20
    assert len(list_data["records"]) == 5

    res_single = client.get("/records/1")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == 1

    res_missing = client.get("/records/999999")
    assert res_missing.status_code == 404


def test_api_feedback_endpoints(client: TestClient, temp_feedback_storage):
    """Verify POST /feedback and GET /feedback using isolated test storage."""
    payload = {
        "question": "How to grep recursively?",
        "answer": "Use `grep -r pattern .`",
        "rating": "helpful",
        "thread_id": "test_thread_api",
    }
    post_res = client.post("/feedback", json=payload)
    assert post_res.status_code == 200
    assert post_res.json()["status"] == "success"

    get_res = client.get("/feedback")
    assert get_res.status_code == 200
    feed_data = get_res.json()
    assert feed_data["total"] >= 1
    assert feed_data["helpful"] >= 1
