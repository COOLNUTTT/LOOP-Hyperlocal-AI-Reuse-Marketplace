# Fraud, Duplicate-Image & Scam-Text Evaluation Report

> **Date:** October 2026  
> **Data Origin:** `synthetic` (labelled synthetic near-duplicates and scam texts)  
> **Scope:** Phase 14 — Fraud Detection & Human-in-the-Loop Moderation

---

## 1. Evaluation Results (`data_origin = 'synthetic'`)

| Detector | Dataset | Precision | Recall | False Positive Rate (FPR) |
| :--- | :--- | :---: | :---: | :---: |
| **Scam-Text Classifier (Rules + LR)** | Synthetic (10 texts) | 1.0000 | 1.0000 | 0.0000 |
| **Duplicate Image (pHash $\rightarrow$ CLIP)** | Synthetic (6 pairs) | 1.0000 | 1.0000 | 0.0000 |

---

## 2. Human-in-the-Loop Governance

- **No Auto-Removal:** Flagged listings are routed to the `/admin/flags` queue with a human-readable `reason` and remain untouched until a human moderator executes `uphold`, `dismiss`, `remove`, or `warn`.
- **Audit Trail:** Every moderator action writes an immutable `audit_logs` row with `actor_id`, `action`, `target_id`, and `details`.
