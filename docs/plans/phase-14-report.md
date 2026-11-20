# Phase 14: Fraud, Duplicates, Scam Text & Moderation Completion Report

> **Date:** October 2026  
> **Status:** Completed  
> **Scope:** Duplicate/Stolen Image Detection, Price Anomaly Rules, Scam-Text Classifier, Human-in-the-Loop Moderation & Audit Logs

---

## 1. Executive Summary

Phase 14 implements fraud detection and human-in-the-loop moderation per `ROADMAP.md` Phase 14:
1. **Fraud & Scam Detection (`ml/src/fraud_detector.py`):**
   - Two-stage duplicate/stolen-image detection: perceptual hash Hamming distance $\rightarrow$ 512-d embedding cosine similarity re-check.
   - Price-anomaly rule flagging $<0.25\times$ or $>3.5\times$ category/subtype median.
   - Logistic-regression-style scam-text classifier producing human-readable reasons.
   - **No auto-removal:** flagged listings are queued for human moderator review.
2. **Moderation, Audit Logs & Model Health (`apps/api/app/routers/moderation.py`, `apps/api/app/services/moderation_service.py`, `apps/api/app/models/audit.py`):**
   - `/admin/flags` queue, `/admin/flags/{id}/action` (`uphold`, `dismiss`, `remove`, `warn`) writing immutable `audit_logs` rows, and `/admin/model-health` returning confidence histograms and drift status.
3. **Synthetic Evaluation (`ml/src/eval_fraud.py`, `ml/reports/fraud_moderation/report.md`):**
   - Evaluated on synthetic near-duplicates and labelled scam texts (`data_origin='synthetic'`), achieving `Precision = 1.0`, `Recall = 1.0`, `FPR = 0.0`.
4. **Acceptance Testing:**
   - `apps/api/tests/test_fraud_moderation_acceptance.py`: All 4 acceptance tests passed.
