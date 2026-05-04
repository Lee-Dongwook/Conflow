"""Tests for the root health endpoint."""

from http import HTTPStatus

from fastapi.testclient import TestClient
from main import app


def test_health_check_returns_ok() -> None:
    """GET / should return 200 and a static JSON body."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"MESSAGE": "OK"}
