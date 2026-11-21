# Phase 18: Validation, Hardening, User Study & Submission (Milestone M4) Implementation Plan

> **Goal:** Complete final validation, 3-journey end-to-end integration & latency benchmarking, licence/security audit (confirming zero AGPL/GPL components and 100% copyright headers), reproducible user-study statistical analysis pipeline (`paired t-test`, `Wilcoxon`, `SUS`, effect sizes) + 5-component ablation study, master figure generator (`ml/reports/make_figures.py`), full research paper draft (`docs/PAPER_DRAFT.md`) with claim audit, demo script (`docs/DEMO_SCRIPT.md`), and copyright filing package (`docs/COPYRIGHT_FILING_PACKAGE.md`) per `ROADMAP.md` Phase 18, `PAPER_PLAN.md`, and `IP_AND_COMPLIANCE.md`:
> 1. System Validation, 3-Journey E2E & Security/Licence Audit (`ml/src/eval_system_validation.py`, `scripts/audit_licenses_and_security.py`):
>    - Verify the 3 main journeys (`list`, `find/buy`, `swap`) + `moderation`, measure p50/p95 latency and throughput, verify RLS coverage across all migrations (`0001`–`0009`), confirm zero AGPL/GPL components, and enforce copyright headers on 100% of source files.
> 2. Reproducible User-Study Analysis & Ablation Suite (`ml/src/eval_user_study_and_ablations.py`, `ml/reports/user_study/`, `ml/reports/ablations/`):
>    - Statistical analysis pipeline computing paired $t$-test, Wilcoxon signed-rank statistic, Cohen's $d$, 95% CIs, and SUS score; clearly marks unmeasured live student metrics as `TBD (not yet measured on live participants)` while providing a clearly labelled synthetic power-analysis verification cohort (`data_origin='simulated'`).
>    - 5-component ablation study (`ML_SPEC.md` §14): semantic search $\rightarrow$ FTS, AI draft $\rightarrow$ manual, explanations $\rightarrow$ removed, scrubber $\rightarrow$ disabled, active learning $\rightarrow$ static seed.
> 3. Master Figure Script, Model Cards & Demo Script (`ml/reports/make_figures.py`, `ml/model_cards/*.md`, `docs/DEMO_SCRIPT.md`):
>    - `ml/reports/make_figures.py` regenerates and hashes all report figures into `ml/reports/figure_manifest.json`.
>    - Complete model cards for `privacy_scrubber`, `semantic_search`, and `fraud_scam_detector` (joining `product_recognition`, `condition_grader`, and `price_estimator`).
> 4. Paper Draft, Claim Audit & Copyright Filing Package (`docs/PAPER_DRAFT.md`, `docs/COPYRIGHT_FILING_PACKAGE.md`):
>    - Assemble 10-section paper draft tracing every metric to a logged run ID/file and prepare the Indian Copyright Office literary/software filing package.
> 5. Phase 18 Acceptance Tests (`apps/api/tests/test_phase18_submission_acceptance.py`), Phase 18 Completion Report (`docs/plans/phase-18-report.md`), and full CI pipeline verification.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p18-task-1 | 3-journey E2E validation, p50/p95 load benchmark & AGPL/GPL licence/security audit | completed | Zero AGPL/GPL; 100% copyright headers |
| p18-task-2 | Reproducible user-study statistical pipeline (t-test/Wilcoxon/SUS) & 5-component ablations | completed | Live study marked TBD; synthetic labelled simulated |
| p18-task-3 | Master figure generator (`ml/reports/make_figures.py`), model cards & `docs/DEMO_SCRIPT.md` | completed | Traceable SHA-256 figure manifest |
| p18-task-4 | Research paper assembly (`docs/PAPER_DRAFT.md`), claim audit & `docs/COPYRIGHT_FILING_PACKAGE.md` | completed | Matches `PAPER_PLAN.md` §3–§9 & `IP_AND_COMPLIANCE.md` §6 |
| p18-task-5 | Acceptance tests, Phase 18 completion report & full CI pipeline verification | completed | All Milestone M4 acceptance criteria passed |
