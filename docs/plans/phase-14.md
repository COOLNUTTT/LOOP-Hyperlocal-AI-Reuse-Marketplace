# Phase 14: Fraud, Duplicates, Scam Text & Moderation Implementation Plan

> **Goal:** Implement fraud detection (duplicate/stolen images, price anomalies, scam-text classification), human-in-the-loop moderation queue with audit logging, model-health monitoring, and synthetic evaluation per `ROADMAP.md` Phase 14:
> 1. Fraud & Scam Detection Engine (`ml/src/fraud_detector.py`):
>    - Duplicate/stolen-image detection (perceptual hash distance $\rightarrow$ 512-d embedding cosine re-check).
>    - Price-anomaly rule (flags extreme underpricing $< 0.25\times$ or overpricing $> 3.5\times$ category-subtype median).
>    - Scam-text classifier (baseline keyword rules + TF-IDF / Logistic Regression style scoring) with human-readable reasons.
>    - **No auto-removal**: flagged listings enter the moderation queue for human decision.
> 2. Moderation & Audit Log API (`apps/api/app/routers/moderation.py`):
>    - Flag queue with evidence & human-readable reason.
>    - Moderator actions (`uphold`, `dismiss`, `remove`, `warn`) that write an `audit_logs` record on every action.
>    - Model-health endpoint (`/admin/model-health`) returning confidence histograms and drift indicators.
> 3. Synthetic Evaluation (`ml/src/eval_fraud.py` & `ml/reports/fraud_moderation/report.md`):
>    - Evaluate precision, recall, and FPR on synthetic near-duplicates and labelled scam texts, clearly labelled as `data_origin='synthetic'`.
> 4. Automated acceptance tests verifying flag creation, human-in-the-loop non-auto-removal, audit log creation, and evaluation metrics.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p14-task-1 | Fraud, duplicate-image, price-anomaly & scam-text engine (`ml/src/fraud_detector.py`) | completed | Human-readable reasons; no auto-removal |
| p14-task-2 | Moderation queue, audit_logs & model-health router (`apps/api/app/routers/moderation.py`) | completed | Uphold/dismiss/remove/warn + audit trail |
| p14-task-3 | Synthetic evaluation (precision/recall/FPR) & report | completed | Clearly labelled `data_origin='synthetic'` |
| p14-task-4 | Acceptance tests & Phase 14 completion report | completed | Verify all Phase 14 acceptance criteria |
