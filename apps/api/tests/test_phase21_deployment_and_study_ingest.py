# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Phase 21 (Tracks D & E) Acceptance Tests: User-Study CSV Ingestion & Deployment Manifests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from ml.src.eval_user_study_and_ablations import analyze_user_study_csv
from scripts.audit_licenses_and_security import run_license_and_security_audit

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_user_study_csv_ingestion_and_paired_statistics() -> None:
    """Verify `analyze_user_study_csv` computes paired t-test, Wilcoxon, Cohen's d, and SUS."""
    tpl_csv = REPO_ROOT / "ml" / "data" / "templates" / "user_study_responses_template.csv"
    assert tpl_csv.exists()

    res = analyze_user_study_csv(tpl_csv)
    assert res["n_participants"] == 10
    assert res["data_origin"] == "simulated"
    assert res["pii_check_passed"] is True

    t_stats = res["listing_time_seconds"]
    assert t_stats["mean_treatment"] < t_stats["mean_control"]
    assert t_stats["paired_t_stat"] < -10.0
    assert t_stats["cohens_d"] < -1.0

    tr_stats = res["trust_likert_1_to_7"]
    assert tr_stats["mean_treatment"] > tr_stats["mean_control"]
    assert tr_stats["paired_t_stat"] > 5.0

    sus = res["sus_score_0_to_100"]
    assert sus["mean"] > sus["benchmark_threshold"]


def test_user_study_csv_pii_guard_rejects_identifiers(tmp_path: Path) -> None:
    """Verify `analyze_user_study_csv` rejects CSVs with prohibited PII columns (`email`)."""
    bad_csv = tmp_path / "contaminated_study.csv"
    bad_csv.write_text(
        "participant_anon_id,email,time_ai_sec,time_manual_sec,trust_explained_1_7,trust_blackbox_1_7,sus_score_0_100,data_origin\n"
        "LOOP-STU-001,student@adypu.edu.in,42.0,140.0,6.0,4.0,82.5,simulated\n"
        "LOOP-STU-002,student2@adypu.edu.in,45.0,145.0,6.0,4.0,80.0,simulated\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="PII_COLUMN_PROHIBITED"):
        analyze_user_study_csv(bad_csv)


def test_free_tier_deployment_manifests_and_runbook_exist() -> None:
    """Verify Supabase SQL bootstrap, Render blueprint, Vercel config, and deployment runbook."""
    supa_sql = REPO_ROOT / "infra" / "supabase" / "setup_storage_and_realtime.sql"
    render_yaml = REPO_ROOT / "render.yaml"
    vercel_json = REPO_ROOT / "apps" / "web" / "vercel.json"
    runbook_md = REPO_ROOT / "docs" / "DEPLOYMENT_AND_USER_STUDY_RUNBOOK.md"

    assert supa_sql.exists()
    assert render_yaml.exists()
    assert vercel_json.exists()
    assert runbook_md.exists()

    sql_text = supa_sql.read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS postgis;" in sql_text
    assert "CREATE EXTENSION IF NOT EXISTS vector;" in sql_text
    assert "listing-images" in sql_text
    assert "supabase_realtime" in sql_text

    render_text = render_yaml.read_text(encoding="utf-8")
    assert "/api/v1/health" in render_text
    assert "alembic upgrade head" in render_text

    vercel_data = json.loads(vercel_json.read_text(encoding="utf-8"))
    assert vercel_data["framework"] == "nextjs"
    assert len(vercel_data["headers"]) >= 2


def test_phase21_license_and_copyright_header_audit() -> None:
    """Verify 100% copyright headers and zero AGPL/GPL packages across all 21 phases."""
    audit = run_license_and_security_audit(REPO_ROOT)
    assert audit["audit_passed"] is True
    assert audit["agpl_gpl_dependencies_found"] == 0
    assert audit["missing_headers"] == []
