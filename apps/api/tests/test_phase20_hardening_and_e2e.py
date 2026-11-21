# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Phase 20 (Track C) Acceptance Tests: Supabase Wiring, Coarse Map, Playwright E2E & Locust."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient
from infra.load.locustfile import (
    LOAD_TEST_SLA_TARGETS,
    LOOPMarketplaceUser,
    get_registered_load_tasks,
)
from scripts.audit_licenses_and_security import run_license_and_security_audit

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
client = TestClient(app)


def test_supabase_client_scrubbed_guard_and_chat_safety_rules() -> None:
    """Verify `supabaseClient.ts` enforces `LISTING_NOT_SCRUBBED`, Realtime, and scam alerts."""
    supa_path = REPO_ROOT / "apps" / "web" / "lib" / "supabaseClient.ts"
    chat_thread_path = REPO_ROOT / "apps" / "web" / "app" / "chat" / "[listingId]" / "page.tsx"

    assert supa_path.exists()
    assert chat_thread_path.exists()

    supa_text = supa_path.read_text(encoding="utf-8")
    assert "LISTING_NOT_SCRUBBED" in supa_text
    assert "subscribeToListingChat" in supa_text
    assert "evaluateChatSafetyWarning" in supa_text
    assert "upi_qr_receive_scam" in supa_text

    chat_text = chat_thread_path.read_text(encoding="utf-8")
    assert "subscribeToListingChat" in chat_text
    assert "evaluateChatSafetyWarning" in chat_text


def test_coarse_area_map_geohash5_privacy_and_odbl_attribution() -> None:
    """Verify `CoarseAreaMap.tsx` enforces `geohash5 <= 5` and OpenStreetMap ODbL attribution."""
    map_path = REPO_ROOT / "apps" / "web" / "components" / "CoarseAreaMap.tsx"
    browse_path = REPO_ROOT / "apps" / "web" / "app" / "browse" / "page.tsx"

    assert map_path.exists()
    map_text = map_path.read_text(encoding="utf-8")
    assert "sanitizeGeohash5" in map_text
    assert ".slice(0, 5)" in map_text
    assert "OpenStreetMap contributors (ODbL)" in map_text

    browse_text = browse_path.read_text(encoding="utf-8")
    assert "CoarseAreaMap" in browse_text


def test_playwright_360px_config_and_four_e2e_journeys() -> None:
    """Verify `playwright.config.ts` (360px viewport) and `e2e/loop-journeys.spec.ts`."""
    pw_cfg_path = REPO_ROOT / "apps" / "web" / "playwright.config.ts"
    pw_spec_path = REPO_ROOT / "apps" / "web" / "e2e" / "loop-journeys.spec.ts"

    assert pw_cfg_path.exists()
    assert pw_spec_path.exists()

    cfg_text = pw_cfg_path.read_text(encoding="utf-8")
    assert "width: 360" in cfg_text
    assert "mobile-360px" in cfg_text

    spec_text = pw_spec_path.read_text(encoding="utf-8")
    for journey_id in (
        "journey-1-snap-to-list",
        "journey-2-discovery-and-coarse-map",
        "journey-3-chat-swap-and-impact",
        "journey-4-moderation-and-active-learning",
    ):
        assert journey_id in spec_text


def test_locust_load_profile_and_live_sla_execution() -> None:
    """Verify `infra/load/locustfile.py` tasks and execute load cycle under SLA (< 1000 ms)."""
    tasks = get_registered_load_tasks()
    assert len(tasks) == 5
    assert LOAD_TEST_SLA_TARGETS["p95_max_ms"] <= 1000.0

    # Execute a simulated user cycle against FastAPI TestClient
    user = LOOPMarketplaceUser()
    user.client = client

    t0 = time.perf_counter()
    user.check_onnx_and_health()
    user.estimate_conformal_price()
    user.analyze_photos_snap_to_list()
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < LOAD_TEST_SLA_TARGETS["p95_max_ms"]


def test_phase20_license_and_copyright_header_audit() -> None:
    """Verify 100% copyright headers and zero AGPL/GPL packages after Phase 20 additions."""
    audit = run_license_and_security_audit(REPO_ROOT)
    assert audit["audit_passed"] is True
    assert audit["agpl_gpl_dependencies_found"] == 0
    assert audit["missing_headers"] == []
