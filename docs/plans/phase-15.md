# Phase 15: Active Learning Loop (Human-in-the-Loop) Implementation Plan

> **Goal:** Implement the human-in-the-loop active learning pipeline, anti-poisoning eligibility rules, end-to-end retraining with gated promotion and rollback on frozen test sets, multi-seed learning-curve experiments (including 10% and 20% label-noise variants) with error-band figures, and the admin view for corrections stats and model versions per `ROADMAP.md` Phase 15 and `ML_SPEC.md` §7:
> 1. Database Model & Migration (`apps/api/app/models/model_version.py`, `apps/api/alembic/versions/0007_model_versions_and_audit.py`):
>    - `model_versions` table storing version metadata, ONNX export path, primary & per-class metrics, baseline metrics, `trained_on_hash`, `is_active`, and `promoted_at` with RLS enabled.
> 2. Eligibility Filter, Anti-Poisoning & Retraining Engine (`ml/src/active_learning/retrain.py`, `ml/src/retrain.py`, `apps/api/app/services/correction_service.py`):
>    - Strict anti-poisoning rules (verified/trusted user with completed trades or admin override, price within 3x MAD / category-subtype median bounds, conflicting corrections on the same listing+field deduplicated to keep the latest).
>    - Frozen test-set hash manifest (`ml/data/manifests/frozen_test_hashes.json`) and strict leakage guard preventing any test-set item from entering retraining data.
>    - End-to-end `retrain_from_corrections` for `product_recognition`, `condition_grader`, and `price_estimator` with gated promotion (candidate must beat active model on primary metric by margin without class regression) and rollback support.
> 3. Active Learning Experiment & Error-Band Figure (`ml/src/eval_active_learning.py`, `ml/reports/active_learning/`):
>    - Compare `random`, `uncertainty`, and `correction_stream` strategies across $\ge 5$ seeds (`[42, 101, 202, 303, 404]`) from a 20% seed training set over batches `0, 25, 50, 100, 200, 400`, plus 10% and 20% label-noise variants.
>    - Produce SVG figure (`active_learning_curves_synthetic.svg`) with error bands and a clearly labelled `"Simulated Corrections (data_origin='simulated')"` caption, plus JSON metrics and markdown report.
> 4. Admin Endpoints & Admin View (`apps/api/app/routers/moderation.py`, `apps/web/app/admin/page.tsx`):
>    - `GET /admin/corrections/stats`, `GET /admin/models`, `POST /admin/models/{name}/promote`, and `POST /admin/models/{name}/rollback`.
>    - Responsive `360px` Admin UI displaying corrections stats per field and model versions with gated promotion and rollback controls.
> 5. Automated Acceptance Tests (`apps/api/tests/test_active_learning_acceptance.py`) & CI verification.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p15-task-1 | `ModelVersion` model & Alembic migration `0007_model_versions_and_audit` with RLS | completed | Schema-exact `model_versions` table |
| p15-task-2 | Anti-poisoning filter, frozen test-set hash guard, `retrain.py` & gated promotion/rollback | completed | Recognition, condition & price retraining |
| p15-task-3 | Multi-seed active learning experiment (3 strategies + 10%/20% noise) & error-band figure | completed | Clearly labelled `Simulated Corrections` |
| p15-task-4 | Admin API endpoints (`/admin/corrections/stats`, `/admin/models/*`) & Next.js Admin page | completed | Responsive 360px admin dashboard |
| p15-task-5 | Acceptance tests, Phase 15 completion report & full CI pipeline verification | completed | All Phase 15 acceptance criteria passed |
