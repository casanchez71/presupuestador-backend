"""Health endpoint tests using FastAPI TestClient.

Note: These tests mock Supabase since we don't have credentials in CI.
"""

import os

import pytest

# Set required env vars before importing app
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert "timestamp" in data


def test_landing_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Presupuestador" in response.text


def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200
