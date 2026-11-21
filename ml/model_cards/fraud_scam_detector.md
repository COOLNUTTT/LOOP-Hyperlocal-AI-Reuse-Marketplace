# Model Card: Fraud, Duplicate-Image & Scam-Text Detector (`fraud_scam_detector`)

- **Version:** `v1.0.0`
- **License:** Permissive (MIT / BSD-3-Clause)
- **Data Origin:** Evaluated on synthetic near-duplicates and labelled scam texts (`data_origin='simulated'`)

## 1. Intended Use & Architecture
- **Duplicate / Stolen Image Detection (Algorithmic):** Two-stage check using 64-bit perceptual hash Hamming distance ($\le 10$) followed by 512-d embedding cosine similarity ($\ge 0.92$).
- **Price-Anomaly Detection (Rule-Based):** Flags listings priced $< 0.25\times$ or $> 3.5\times$ the category/subtype median.
- **Scam-Text Classifier (ML + Rules):** Keyword risk rules + TF-IDF logistic scoring for UPI QR payment traps, advance fee requests, and off-platform phishing links.
- **Human-in-the-Loop Governance:** Never auto-removes a listing; all flags enter `/admin/flags` with a human-readable reason and require a moderator decision (`uphold`, `dismiss`, `remove`, `warn`) logged to `audit_logs`.

## 2. Evaluation Metrics (`ml/reports/fraud_moderation/report.md`, `data_origin='synthetic'`)
| Task | Precision | Recall | False Positive Rate (FPR) |
| :--- | :--- | :--- | :--- |
| Synthetic Near-Duplicate Images | 1.0000 | 1.0000 | 0.0000 |
| Synthetic Scam-Text Corpus | 1.0000 | 1.0000 | 0.0000 |

## 3. Limitations
- Evaluated on synthetic near-duplicates and scam templates; adversarial paraphrasing or heavily re-photographed screens require continuous moderator feedback.
