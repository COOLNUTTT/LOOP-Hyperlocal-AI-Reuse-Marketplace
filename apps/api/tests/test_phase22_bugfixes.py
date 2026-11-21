# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Phase 22 Regression Tests: Verify all 9 full-stack bugfixes."""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies.auth import AuthenticatedUser, get_current_db_user
from app.main import app
from app.models.identity import User

REPO_ROOT = Path(__file__).resolve().parents[3]
client = TestClient(app)


def test_health_mounted_at_both_root_and_api_v1() -> None:
    """Verify both `/health` (CI/Docker) and `/api/v1/health` (Render/Locust) return 200."""
    r1 = client.get("/health")
    r2 = client.get("/api/v1/health")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["status"] == "healthy"
    assert r2.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_current_db_user_resolves_authenticated_user_and_mock_user() -> None:
    """Verify `get_current_db_user` resolves `AuthenticatedUser` from DB and passes `User` mocks."""
    # 1. Compatibility with existing unit tests that mock `get_current_user` with a User instance
    mock_user = User(
        id=uuid.uuid4(),
        auth_uid=uuid.uuid4(),
        display_name="Mock User",
        area_name="Lohegaon",
        geohash5="tek3x",
        is_verified=True,
        role="admin",
    )
    resolved_mock = await get_current_db_user(auth_user=mock_user, db=None)
    assert resolved_mock is mock_user
    assert resolved_mock.role == "admin"

    # 2. Real JWT path: AuthenticatedUser -> queries DB by auth_uid and returns User
    auth_uid = uuid.uuid4()
    auth_user = AuthenticatedUser(
        auth_uid=auth_uid,
        email="student@adypu.edu.in",
        is_confirmed=True,
        raw_payload={"user_metadata": {"display_name": "Sameer"}},
    )
    db_user = User(
        id=uuid.uuid4(),
        auth_uid=auth_uid,
        display_name="Sameer",
        area_name="Lohegaon",
        geohash5="tek3x",
        is_verified=True,
        role="user",
    )
    fake_result = MagicMock()
    fake_result.scalar_one_or_none.return_value = db_user
    fake_db = AsyncMock()
    fake_db.execute.return_value = fake_result

    resolved_real = await get_current_db_user(auth_user=auth_user, db=fake_db)
    assert resolved_real is db_user
    assert resolved_real.id == db_user.id


def test_frontend_api_rewrites_sell_publish_flow_and_worker_ts() -> None:
    """Verify Next.js `/api/v1` rewrites, `/sell` image+publish flow, and worker TS types."""
    next_cfg = (REPO_ROOT / "apps" / "web" / "next.config.mjs").read_text(encoding="utf-8")
    assert "rewrites()" in next_cfg
    assert "/api/v1/:path*" in next_cfg

    sell_page = (REPO_ROOT / "apps" / "web" / "app" / "sell" / "page.tsx").read_text(
        encoding="utf-8"
    )
    assert "/images" in sell_page
    assert "/publish" in sell_page

    worker_ts = (REPO_ROOT / "apps" / "web" / "lib" / "scrubber.worker.ts").read_text(
        encoding="utf-8"
    )
    assert "WorkerGlobalScopeLike" in worker_ts
    assert "workerScope.postMessage(response)" in worker_ts


def test_locust_uses_valid_swap_proposals_endpoint() -> None:
    """Verify Locust load harness uses `/api/v1/swap/proposals` instead of 404 `/swap/cycles`."""
    locust_text = (REPO_ROOT / "infra" / "load" / "locustfile.py").read_text(encoding="utf-8")
    assert "/api/v1/swap/proposals" in locust_text
    assert "/api/v1/swap/cycles" not in locust_text


def test_admin_service_purges_listing_image_prefixes() -> None:
    """Verify DPDP `purge_user_storage` accepts and purges `listings/{listing_id}/` prefixes."""
    admin_text = (REPO_ROOT / "apps" / "api" / "app" / "services" / "admin_service.py").read_text(
        encoding="utf-8"
    )
    user_text = (REPO_ROOT / "apps" / "api" / "app" / "services" / "user_service.py").read_text(
        encoding="utf-8"
    )
    assert "listing_ids" in admin_text
    assert "listings/{lid}/" in admin_text
    assert "listing_ids=listing_ids" in user_text
