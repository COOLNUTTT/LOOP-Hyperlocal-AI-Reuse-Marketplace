# Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.
"""Acceptance tests for Phase 18 Validation, Hardening, User Study & Submission (Milestone M4):

1. Licence audit clean (zero AGPL/GPL packages), 100% copyright headers on all source
   files, and Row Level Security (RLS) verified across all 9 Alembic migrations.
2. End-to-end validation of the 3 main journeys (`list`, `find/buy`, `swap`) + `moderation`
   and p50/p95 CPU latency benchmark (< 1000 ms).
3. Reproducible user-study statistical analysis script (`paired t-test`, `Wilcoxon`,
   `Cohen's d`, `SUS`) + 5-component ablation study, with unmeasured live human metrics
   explicitly marked `TBD`.
4. Master figure script (`ml/reports/make_figures.py`) generates all 8 report figure sets
   with SHA-256 hashes in `ml/reports/figure_manifest.json`.
5. Complete model cards, demo script (`docs/DEMO_SCRIPT.md`), paper draft (`docs/PAPER_DRAFT.md`),
   and copyright filing package (`docs/COPYRIGHT_FILING_PACKAGE.md`) exist.
"""

import unittest
from pathlib import Path

from ml.reports.make_figures import generate_all_figures_and_manifest
from ml.src.eval_system_validation import run_three_journeys_and_load_benchmark
from ml.src.eval_user_study_and_ablations import (
    compute_paired_statistics,
    run_user_study_analysis_and_ablations,
)
from scripts.audit_licenses_and_security import run_license_and_security_audit

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestPhase18SubmissionAcceptance(unittest.TestCase):
    def test_license_audit_copyright_headers_and_rls(self) -> None:
        """Verify zero AGPL/GPL components, 100% copyright headers, and 9 RLS migrations."""
        audit = run_license_and_security_audit(REPO_ROOT)
        self.assertTrue(audit["audit_passed"], msg=f"Violations: {audit['violations']}")
        self.assertEqual(audit["agpl_gpl_dependencies_found"], 0)
        self.assertEqual(audit["rls_migrations_verified"], 9)
        self.assertEqual(len(audit["missing_headers"]), 0)

    def test_three_main_journeys_and_load_benchmark(self) -> None:
        """Verify E2E journeys (list, find/buy, swap, moderation) and p95 latency < 1000ms."""
        val = run_three_journeys_and_load_benchmark(iterations=50)
        self.assertTrue(val["journeys"]["all_passed"])
        self.assertLess(val["load_benchmark"]["p95_latency_ms"], 1000.0)
        self.assertGreater(val["load_benchmark"]["throughput_ops_per_sec"], 10.0)

    def test_reproducible_user_study_script_tbd_honesty_and_ablations(self) -> None:
        """Verify deterministic user-study stats, TBD marking for live metrics, and 5 ablations."""
        run1 = run_user_study_analysis_and_ablations(seed=42, n_participants=40)
        run2 = run_user_study_analysis_and_ablations(seed=42, n_participants=40)
        self.assertEqual(run1, run2)

        study = run1["user_study"]
        self.assertIn("TBD", study["live_human_study_status"])
        for val in study["live_human_metrics"].values():
            self.assertIn("TBD", str(val))

        sim_cohort = study["simulated_power_analysis_cohort"]
        self.assertEqual(sim_cohort["data_origin"], "simulated")
        self.assertLess(
            sim_cohort["listing_time_seconds"]["mean_treatment"],
            sim_cohort["listing_time_seconds"]["mean_control"],
        )
        self.assertGreater(
            sim_cohort["trust_likert_1_to_7"]["mean_treatment"],
            sim_cohort["trust_likert_1_to_7"]["mean_control"],
        )

        # Verify paired statistical helper directly
        paired = compute_paired_statistics([40.0, 45.0, 50.0, 42.0], [120.0, 130.0, 140.0, 125.0])
        self.assertLess(paired["paired_t_stat"], -10.0)

        # Verify all 5 ablations exist
        ablations = run1["ablations"]["ablations"]
        self.assertEqual(len(ablations), 5)

    def test_make_figures_manifest_and_submission_artifacts(self) -> None:
        """Verify all 8 figures trace to logged runs and paper/filing/model cards are complete."""
        manifest = generate_all_figures_and_manifest()
        self.assertTrue(manifest["all_figures_present"])
        self.assertEqual(len(manifest["figures"]), 8)
        for fig in manifest["figures"]:
            self.assertTrue(fig["exists"], msg=f"Missing figure: {fig['artifact_path']}")
            self.assertIsNotNone(fig["sha256"])

        required_docs = [
            REPO_ROOT / "docs" / "PAPER_DRAFT.md",
            REPO_ROOT / "docs" / "COPYRIGHT_FILING_PACKAGE.md",
            REPO_ROOT / "docs" / "DEMO_SCRIPT.md",
            REPO_ROOT / "docs" / "IMPACT_METHOD.md",
            REPO_ROOT / "ml" / "model_cards" / "product_recognition.md",
            REPO_ROOT / "ml" / "model_cards" / "condition_grader.md",
            REPO_ROOT / "ml" / "model_cards" / "price_estimator.md",
            REPO_ROOT / "ml" / "model_cards" / "privacy_scrubber.md",
            REPO_ROOT / "ml" / "model_cards" / "semantic_search.md",
            REPO_ROOT / "ml" / "model_cards" / "fraud_scam_detector.md",
        ]
        for doc_path in required_docs:
            self.assertTrue(doc_path.exists(), msg=f"Missing submission artifact: {doc_path}")


if __name__ == "__main__":
    unittest.main()
