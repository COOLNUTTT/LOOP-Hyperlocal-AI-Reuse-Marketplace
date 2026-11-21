# Phase 21 (Tracks D & E): Anonymised User-Study CSV Ingestion CLI & Free-Tier Production Deployment Plan

> **Goal:** Complete the final two engineering tracks (**Track D: User-Study CSV Ingestion & PII-Guard Analysis CLI** and **Track E: Free-Tier Cloud Deployment Manifests for Supabase, Render & Vercel**) per `ROADMAP.md` Phase 18, `PAPER_PLAN.md` §§5–6, and `AGENTS.md` §8.

---

## 1. Architecture & Scope

1. **Track D — Anonymised User-Study CSV Template & CLI Ingestion (`ml/data/templates/user_study_responses_template.csv`, `ml/src/eval_user_study_and_ablations.py`):**
   - Create `ml/data/templates/user_study_responses_template.csv` with strictly anonymised schema: `participant_anon_id,time_ai_sec,time_manual_sec,trust_explained_1_7,trust_blackbox_1_7,sus_score_0_100,data_origin`.
   - Add `analyze_user_study_csv(csv_path: Path)` and `--csv` CLI argument to `ml/src/eval_user_study_and_ablations.py`:
     - **PII Guard (`AGENTS.md` §8):** Immediately rejects any CSV that contains prohibited identifier columns (`name`, `email`, `phone`, `roll_no`, `student_id`, `address`).
     - Computes paired $t$-test, two-sided $p$-value, 95% confidence interval, Cohen's $d$, Wilcoxon signed-rank $W$ and $z$, and SUS mean/SD/median/IQR from the ingested rows.
     - Preserves the default `TBD (not yet measured on live participants)` marker whenever no live human CSV has been ingested.

2. **Track E — Free-Tier Production Deployment Manifests (`apps/web/vercel.json`, `render.yaml`, `infra/supabase/setup_storage_and_realtime.sql`, `docs/DEPLOYMENT_AND_USER_STUDY_RUNBOOK.md`):**
   - `infra/supabase/setup_storage_and_realtime.sql`: Idempotent SQL bootstrap enabling `postgis` and `vector` extensions, creating the `listing-images` Storage bucket with RLS policies, and adding `public.messages` to the `supabase_realtime` publication.
   - `render.yaml`: Free-tier Render web-service blueprint for `apps/api` running `alembic upgrade head` and `uvicorn app.main:app` with healthcheck `/api/v1/health`.
   - `apps/web/vercel.json`: Next.js PWA Vercel configuration with immutable caching for `/models/*.onnx` and security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`).
   - `docs/DEPLOYMENT_AND_USER_STUDY_RUNBOOK.md`: Complete runbook for deploying the live public demo URL and executing the 30–50 student user study.

3. **Acceptance Tests (`apps/api/tests/test_phase21_deployment_and_study_ingest.py`):**
   - Test CSV ingestion on `user_study_responses_template.csv`, verify PII column rejection guard raises `ValueError` on forbidden columns (`email`, `phone`, `name`), verify `vercel.json`, `render.yaml`, and `setup_storage_and_realtime.sql`, and run full licence and copyright header audits.

---

## 2. Task Breakdown

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p21-task-1 | Create `ml/data/templates/user_study_responses_template.csv` & add `analyze_user_study_csv` with PII column guard to `ml/src/eval_user_study_and_ablations.py` | completed | Rejects any CSV with `name`/`email`/`phone`/`roll_no` |
| p21-task-2 | Create `infra/supabase/setup_storage_and_realtime.sql`, `render.yaml`, and `apps/web/vercel.json` | completed | Free-tier deployment manifests for Supabase, Render & Vercel |
| p21-task-3 | Write `docs/DEPLOYMENT_AND_USER_STUDY_RUNBOOK.md` covering live deployment, demo accounts & 30–50 student session protocol | completed | Step-by-step evaluator & pilot checklist |
| p21-task-4 | Write `apps/api/tests/test_phase21_deployment_and_study_ingest.py`, run full test/lint/licence audits, and write `phase-21-report.md` | completed | All 22 acceptance tests + ruff + audits passed |
