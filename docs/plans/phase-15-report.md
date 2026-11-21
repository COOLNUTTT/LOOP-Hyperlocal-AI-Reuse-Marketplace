# Phase 15: Active Learning Loop (Human-in-the-Loop) Completion Report

> **Date:** November 2026  
> **Status:** Completed  
> **Scope:** Anti-Poisoning Eligibility Filter, Conflicting-Correction Deduplication, Frozen Test-Set Leakage Guard, Gated Model Promotion & Rollback, Multi-Seed Learning Curve Experiment (with 10% & 20% Label Noise), and Admin Governance Dashboard

---

## 1. Executive Summary

Phase 15 implements the human-in-the-loop active learning pipeline per `ROADMAP.md` Phase 15 and `ML_SPEC.md` §7:
1. **Database Schema & RLS (`apps/api/app/models/model_version.py`, `apps/api/alembic/versions/0007_model_versions_and_audit.py`):**
   - Added `model_versions` table (`id`, `name`, `version`, `onnx_path`, `metrics`, `baseline_metrics`, `trained_on_hash`, `is_active`, `promoted_at`, `notes`, `created_at`) and `audit_logs` migration with Row Level Security.
2. **Anti-Poisoning Filter, Leakage Guard & Retraining Pipeline (`ml/src/active_learning/retrain.py`, `ml/src/retrain.py`, `apps/api/app/services/correction_service.py`):**
   - **Anti-Poisoning Rules:** Requires verified user status (`is_verified=True` and completed trades $\ge 1$ when present, or admin role) and bounds price overrides within $0.2\times$ to $3.0\times$ of the category/subtype median. Conflicting corrections on the same `(listing_id, field)` are deduplicated to keep only the latest correction.
   - **Frozen Test-Set Hash Guard:** `verify_no_test_set_leakage()` checks all retraining items against `ml/data/manifests/frozen_test_hashes.json` and raises a `ValueError` if any frozen test-set item ever enters retraining data.
   - **Gated Promotion & Rollback:** `retrain_from_corrections()` retrains `product_recognition`, `condition_grader`, and `price_estimator` from `corrections` rows and promotes a candidate **only if** it beats the active model on the primary metric by margin without regressing any class beyond tolerance. `rollback_model_version()` restores the prior version.
3. **Multi-Seed Research Experiment (`ml/src/eval_active_learning.py`, `ml/reports/active_learning/`):**
   - Evaluated `random`, `uncertainty`, and `correction_stream` strategies across 5 seeds (`[42, 101, 202, 303, 404]`) starting from a 20% seed training set over batches `[0, 25, 50, 100, 200, 400]`, plus 10% and 20% label-noise variants.
   - Generated `ml/reports/active_learning/active_learning_curves_synthetic.svg` with shaded $\pm 1\text{ SD}$ error bands and an explicit `"Simulated Corrections (data_origin='simulated')"` caption.
4. **Admin API & Governance View (`apps/api/app/routers/moderation.py`, `apps/web/app/admin/page.tsx`):**
   - Added `GET /admin/corrections/stats`, `GET /admin/models`, `POST /admin/models/{name}/promote`, and `POST /admin/models/{name}/rollback`.
   - Built a mobile-first (`360px` responsive) Admin page (`apps/web/app/admin/page.tsx`) showing corrections stats per field and model versions with gated promotion and rollback controls.
5. **Acceptance Testing (`apps/api/tests/test_active_learning_acceptance.py`):**
   - All 5 Phase 15 acceptance tests passed (`5 passed in 0.75s`).
