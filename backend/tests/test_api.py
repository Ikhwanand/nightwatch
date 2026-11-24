import pytest
from fastapi.testclient import TestClient
from nightwatch.app import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "default_model" in data


def test_recent_incidents_endpoint():
    response = client.get("/api/v1/alerts/recent")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_pending_approvals_endpoint():
    response = client.get("/api/v1/approvals/pending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_audit_logs_endpoint():
    response = client.get("/api/v1/approvals/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_incident_endpoint():
    response = client.delete("/api/v1/alerts/incidents/INC-NONEXISTENT")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_delete_audit_log_endpoint():
    response = client.delete("/api/v1/approvals/audit-logs/999999")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


