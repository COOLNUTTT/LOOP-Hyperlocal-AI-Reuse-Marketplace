# Phase 21 (Tracks D & E): Anonymised User-Study CSV Ingestion CLI & Free-Tier Production Deployment Completion Report

> **Date:** November 2026  
> **Status:** Completed (All engineering tracks **A, B, C, D, E** and Phases **1–21** completed)  
> **Scope:** Anonymised User-Study CSV Template (`ml/data/templates/user_study_responses_template.csv`), PII-Guarded Statistical Analyzer CLI (`ml/src/eval_user_study_and_ablations.py`), Free-Tier Cloud Deployment Manifests (`infra/supabase/setup_storage_and_realtime.sql`, `render.yaml`, `apps/web/vercel.json`), Live Deployment & User-Study Runbook (`docs/DEPLOYMENT_AND_USER_STUDY_RUNBOOK.md`), and Acceptance Tests (`apps/api/tests/test_phase21_deployment_and_study_ingest.py`)

---

## 1. Executive Summary

Phase 21 completes the final two engineering tracks (**Track D** and **Track E**):

1. **Anonymised User-Study CSV Ingestion & PII Column Guard (`ml/src/eval_user_study_and_ablations.py`, `ml/data/templates/user_study_responses_template.csv`):**
   - Created `user_study_responses_template.csv` and added `analyze_user_study_csv(csv_path)` + `--csv` CLI support.
   - Enforces a strict PII column rejection guard (`PII_COLUMN_PROHIBITED`) that blocks any CSV containing identifier headers (`name`, `email`, `phone`, `roll_no`, `student_id`, `prn`, `address`).
   - Computes paired $t$-statistics, two-sided $p$-values, 95% confidence intervals, Cohen's $d$, Wilcoxon signed-rank $W$ & $z$, and SUS mean/SD/median/IQR while preserving the `TBD` marker whenever live human sessions have not yet been ingested.

2. **Free-Tier Production Deployment Manifests & Runbook (`infra/supabase/setup_storage_and_realtime.sql`, `render.yaml`, `apps/web/vercel.json`, `docs/DEPLOYMENT_AND_USER_STUDY_RUNBOOK.md`):**
   - `setup_storage_and_realtime.sql`: Idempotent SQL bootstrap enabling `postgis`, `vector`, the `listing-images` Storage bucket + RLS policies, and the `supabase_realtime` publication on `public.messages`.
   - `render.yaml`: Free-tier FastAPI blueprint running `alembic upgrade head` and `uvicorn app.main:app` with healthcheck `/api/v1/health`.
   - `apps/web/vercel.json`: Next.js 15 PWA configuration with immutable caching for `/models/*.onnx` and security headers.
