# Phase 18: Validation, Hardening, User Study & Submission (Milestone M4) Completion Report

> **Date:** November 2026  
> **Status:** Completed (Completes Milestone **M4: Submission** and all build phases of `ROADMAP.md`)  
> **Scope:** 3-Journey E2E Validation & Load Benchmark, AGPL/GPL Licence & Copyright Header Audit, Reproducible User-Study Statistical Pipeline + 5-Component Ablations, Master Figure Manifest (`make_figures.py`), Complete Model Cards, Research Paper Draft (`docs/PAPER_DRAFT.md`), Demo Script (`docs/DEMO_SCRIPT.md`), and Copyright Filing Package (`docs/COPYRIGHT_FILING_PACKAGE.md`)

---

## 1. Executive Summary

Phase 18 completes validation, hardening, research paper assembly, and submission packaging per `ROADMAP.md` Phase 18, `PAPER_PLAN.md`, and `IP_AND_COMPLIANCE.md`:
1. **End-to-End 3-Journey Validation, Load Benchmark & Security Audit (`ml/src/eval_system_validation.py`, `scripts/audit_licenses_and_security.py`):**
   - Verified the 3 main journeys (`Snap-to-List`, `Find & Buy`, `Multi-Party Swap & Impact`) plus `Fraud & Moderation`.
   - Measured CPU pipeline latency (`p50 < 5 ms`, `p95 < 15 ms`, well under the `1000 ms` target).
   - Confirmed **zero AGPL/GPL packages**, **100% copyright header coverage** across all source files, and **Row Level Security (`RLS`)** across all 9 Alembic migrations (`0001`–`0009`).
2. **Reproducible User-Study Pipeline & 5-Component Ablation Suite (`ml/src/eval_user_study_and_ablations.py`, `ml/reports/user_study/`, `ml/reports/ablations/`):**
   - Implemented paired $t$-test, Wilcoxon signed-rank test, Cohen's $d$, 95% confidence intervals, and SUS usability scoring.
   - Marked unmeasured live human student metrics as `TBD (not yet measured on live participants)` per `AGENTS.md` §8 honesty rules while verifying the pipeline on a `Simulated Power-Analysis Cohort (data_origin='simulated', N=40)`.
   - Executed the 5-component ablation study (`ML_SPEC.md` §14).
3. **Master Figure Manifest, Complete Model Cards & Demo Script (`ml/reports/make_figures.py`, `ml/model_cards/*.md`, `docs/DEMO_SCRIPT.md`):**
   - `ml/reports/make_figures.py` regenerates all 8 report figure sets and logs their SHA-256 digests in `ml/reports/figure_manifest.json`.
   - Completed all 6 model cards (`product_recognition`, `condition_grader`, `price_estimator`, `privacy_scrubber`, `semantic_search`, `fraud_scam_detector`) and the evaluator demo script (`docs/DEMO_SCRIPT.md`).
4. **Research Paper Draft & Copyright Filing Package (`docs/PAPER_DRAFT.md`, `docs/COPYRIGHT_FILING_PACKAGE.md`):**
   - Assembled the 10-section research paper draft (`docs/PAPER_DRAFT.md`) with full claim-audit traceability and prepared the Indian Copyright Office software registration package (`docs/COPYRIGHT_FILING_PACKAGE.md`).
5. **Acceptance Testing (`apps/api/tests/test_phase18_submission_acceptance.py`):**
   - All Phase 18 acceptance tests passed.
