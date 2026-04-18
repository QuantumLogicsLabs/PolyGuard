"""
tests/test_api.py
=================
FastAPI endpoint tests using httpx TestClient.
"""
import pytest
from fastapi.testclient import TestClient

from src.inference.api import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_rules_only_scan_sqli():
    resp = client.post(
        "/scan/rules-only",
        json={
            "code": 'cursor.execute("SELECT * FROM users WHERE id = " + uid)',
            "language": "python",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["finding_count"] >= 1
    types = [f["vuln_type"] for f in data["findings"]]
    assert "sql_injection" in types


def test_rules_only_scan_clean():
    resp = client.post(
        "/scan/rules-only",
        json={"code": "def greet(name):\n    return f'Hello {name}'", "language": "python"},
    )
    assert resp.status_code == 200
    assert resp.json()["finding_count"] == 0


def test_scan_response_shape():
    resp = client.post(
        "/scan/rules-only",
        json={"code": 'api_key = "sk-abc123longersecretkey"', "language": "python"},
    )
    data = resp.json()
    assert "language" in data
    assert "overall_risk" in data
    assert "finding_count" in data
    assert "scan_time_ms" in data
    assert "findings" in data
    if data["findings"]:
        f = data["findings"][0]
        assert "vuln_type" in f
        assert "severity" in f
        assert "confidence" in f
