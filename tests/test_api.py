from fastapi.testclient import TestClient

from app import main
from app.llm import LLMError
from app.schemas import LLMAnalysis

client = TestClient(main.app)

FAKE_ANALYSIS = LLMAnalysis(
    category="billing",
    priority="high",
    summary="Customer was charged twice.",
    suggested_reply="Sorry about that. Could you share the transaction date?",
)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_short_text():
    response = client.post("/tickets/analyze", json={"text": "hi"})
    assert response.status_code == 422


def test_analyze_success(monkeypatch):
    monkeypatch.setattr(main, "analyze_with_llm", lambda text, similar: FAKE_ANALYSIS)
    response = client.post(
        "/tickets/analyze", json={"text": "I was charged twice for my order"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["analysis"]["category"] == "billing"
    assert len(body["similar_tickets"]) == 3


def test_analyze_llm_failure_returns_502(monkeypatch):
    def broken(text, similar):
        raise LLMError("simulated failure")

    monkeypatch.setattr(main, "analyze_with_llm", broken)
    response = client.post(
        "/tickets/analyze", json={"text": "I was charged twice for my order"}
    )
    assert response.status_code == 502

def test_analyze_rejects_too_long_text(monkeypatch):
    monkeypatch.setattr(main, "analyze_with_llm", lambda text, similar: FAKE_ANALYSIS)
    response = client.post("/tickets/analyze", json={"text": "a" * 2001})
    assert response.status_code == 422