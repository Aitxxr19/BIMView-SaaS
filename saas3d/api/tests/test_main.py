import pytest
from fastapi.testclient import TestClient
from test_main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "BIMView API"
    assert response.json()["status"] == "running"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_cors_headers():
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in response.headers
