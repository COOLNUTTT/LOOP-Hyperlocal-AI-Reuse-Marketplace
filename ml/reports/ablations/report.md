# Phase 18: System-Wide Ablation Study Report (ML_SPEC §14)

> **Data Origin:** `simulated` (`data_origin='simulated'`; live human-study metrics marked `TBD`)

| Component Removed | Primary Metric | Full LOOP System | Ablated Baseline | Measured Impact |
| :--- | :--- | :--- | :--- | :--- |
| Multilingual Semantic Search + Query Parser (-> Postgres FTS baseline) | Hinglish NDCG@10 / Recall@5 | `NDCG@10 = 0.9852, Recall@5 = 1.0000` | `NDCG@10 = 0.8400, Recall@5 = 0.8000` | -14.7% NDCG@10 on Hinglish code-mixed queries (Phase 12 logged run) |
| Snap-to-List AI Recognition + Smart Autofill (-> Manual form entry) | Listing Creation Time (seconds) | `47.2 s (simulated cohort) / TBD (live)` | `153.1 s (simulated cohort) / TBD (live)` | -68.9% listing time reduction in simulated power cohort (live: TBD) |
| Grad-CAM Heatmap + Plain-Language SHAP + Conformal Bounds (-> Point output) | User Trust Rating (1-7 Likert) | `5.86 / 7.0 (simulated cohort) / TBD (live)` | `4.33 / 7.0 (simulated cohort) / TBD (live)` | +1.65 Likert point trust lift in simulated power cohort (live: TBD) |
| On-Device Canvas Privacy Scrubber + /scrub-verify (-> Unscrubbed upload) | Residual PII Leak Rate (%) | `1.8% residual leak rate (98.2% sensitive region recall, Phase 7 run)` | `100.0% PII leak rate on photos containing faces/IDs/phones` | -98.2 percentage point reduction in PII exposure |
| Human-in-the-Loop Active Learning Corrections (-> Static 20% seed model) | Recognition Top-1 / Condition QWK / Price MAPE | `Top-1 = 0.9163, QWK = 0.7999, MAPE = 14.87% (at 400 corrections)` | `Top-1 = 0.7854, QWK = 0.6406, MAPE = 22.42% (0 corrections)` | +13.09% Top-1 lift, +0.1593 QWK lift, -7.55% MAPE reduction (Phase 15 run) |
