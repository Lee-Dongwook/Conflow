"""Tests for user CRUD API routes without real database connections."""
# ruff: noqa: I001

from __future__ import annotations

import sys
from datetime import timezone, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture  # noqa: F401
    from _pytest.fixtures import FixtureRequest  # noqa: F401
    from _pytest.logging import LogCaptureFixture  # noqa: F401
    from _pytest.monkeypatch import MonkeyPatch
    from pytest_mock.plugin import MockerFixture  # noqa: F401


def _build_user(**overrides: Any) -> SimpleNamespace:
    """Create a fake user object compatible with UserRead schema."""

    base_user = {
        "uuid": "11111111-1111-4111-8111-111111111111",
        "created_at": datetime.now(timezone.utc),  # noqa: UP017
        "updated_at": datetime.now(timezone.utc),  # noqa: UP017
        "deleted_at": None,
        "name": "conflow",
        "email": "conflow@example.com",
        "profile_image_url": None,
        "role": "user",
        "auth_id": None,
    }
    merged_user = {**base_user, **overrides}
    return SimpleNamespace(**merged_user)


@pytest.fixture
def client() -> TestClient:
    """Create a test client with database dependency overridden."""
    from main import app
    from src.app.core.database import get_async_db

    async def _fake_get_async_db() -> Any:
        yield SimpleNamespace()

    app.dependency_overrides[get_async_db] = _fake_get_async_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_user_returns_201(monkeypatch: MonkeyPatch, client: TestClient) -> None:
    """POST /users should return created user data."""

    async def _fake_create_user(db: object, payload: object) -> SimpleNamespace:
        return _build_user(name="new-user", email="new-user@example.com")

    monkeypatch.setattr("src.app.user.api.create_user", _fake_create_user)

    response = client.post(
        "/users",
        json={
            "name": "new-user",
            "email": "new-user@example.com",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "new-user"
    assert response.json()["email"] == "new-user@example.com"
    assert "uuid" in response.json()


def test_list_users_supports_include_deleted(monkeypatch: MonkeyPatch, client: TestClient) -> None:
    """GET /users should pass include_deleted query option."""

    captured_include_deleted: dict[str, bool] = {"value": False}

    async def _fake_list_users(
        db: object,
        *,
        include_deleted: bool = False,
    ) -> list[SimpleNamespace]:
        captured_include_deleted["value"] = include_deleted
        return [_build_user(), _build_user(uuid="22222222-2222-4222-8222-222222222222")]

    monkeypatch.setattr("src.app.user.api.list_users", _fake_list_users)

    response = client.get("/users?include_deleted=true")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert captured_include_deleted["value"] is True


def test_get_user_returns_404(monkeypatch: MonkeyPatch, client: TestClient) -> None:
    """GET /users/{uuid} should map not found from service layer."""

    async def _fake_get_user_or_404(db: object, user_uuid: str) -> SimpleNamespace:
        raise HTTPException(status_code=404, detail="User not found")

    monkeypatch.setattr("src.app.user.api.get_user_or_404", _fake_get_user_or_404)

    response = client.get("/users/33333333-3333-4333-8333-333333333333")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_returns_200(monkeypatch: MonkeyPatch, client: TestClient) -> None:
    """PATCH /users/{uuid} should return updated user data."""

    async def _fake_update_user(db: object, user_uuid: str, payload: object) -> SimpleNamespace:
        return _build_user(name="updated-user")

    monkeypatch.setattr("src.app.user.api.update_user", _fake_update_user)

    response = client.patch(
        "/users/44444444-4444-4444-8444-444444444444",
        json={"name": "updated-user"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "updated-user"


def test_delete_user_returns_204(monkeypatch: MonkeyPatch, client: TestClient) -> None:
    """DELETE /users/{uuid} should return no content."""

    async def _fake_delete_user(db: object, user_uuid: str) -> None:
        return None

    monkeypatch.setattr("src.app.user.api.delete_user", _fake_delete_user)

    response = client.delete("/users/55555555-5555-4555-8555-555555555555")

    assert response.status_code == 204
    assert response.content == b""
