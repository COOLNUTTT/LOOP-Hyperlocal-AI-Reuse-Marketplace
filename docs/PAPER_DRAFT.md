# LOOP: A Human-in-the-Loop, Explainable, Privacy-Preserving AI Marketplace for Hyperlocal Reuse

**Authors:** Emmanuel George P, Sameer Makani  
**Release Tag:** `paper-v1`  
**Claim-Audit Status (`PAPER_PLAN.md` §9):** Every reported metric traces to a logged run in `ml/reports/` (`figure_manifest.json`). Synthetic and simulated evaluations are explicitly labelled `data_origin='simulated'`. Live human user-study measurements are marked `TBD (not yet measured on live participants)`.

---

## Abstract

Peer-to-peer reuse within closed hyperlocal communities (university campuses, student hostels, and residential housing societies) suffers from three structural frictions: high listing effort, privacy leaks in user-uploaded photographs, and low trust in opaque algorithmic valuations. We present **LOOP**, an installable progressive web application and human-in-the-loop AI marketplace covering Electronics, Furniture, Books, and Hobbies. First, LOOP enforces **client-side photo privacy scrubbing** before upload, redacting faces, ID cards, number plates, Indian phone numbers, and postal addresses with `98.2%` macro recall (`1.8%` residual leak rate on the staged test set). Second, its **Snap-to-List pipeline** pairs linear-probe product recognition (`92.6%` top-1 accuracy, `0.918` macro-F1), ordinal expected-value condition grading (`0.812` quadratic weighted kappa with dismissible Grad-CAM heatmaps), and split-conformal quantile price estimation (`81.4%` empirical coverage at `80%` nominal target, `14.2%` MAPE, and plain-language top-3 SHAP explanations). Third, seller edits to AI predictions feed an **anti-poisoning active learning loop** with gated promotion on a frozen test set (`+13.09%` recognition accuracy lift and `-7.55%` price MAPE reduction over `400` simulated corrections across 5 seeds). Finally, LOOP integrates an **algorithmic $\le 3$-way CP-SAT barter swap solver**, a **cited range-based LCA impact estimator** ($d \in [0.30, 0.80]$), and an **agent-based marketplace simulator** ($N = 100 \rightarrow 10,000$ synthetic agents).

---

## 1. Introduction

### 1.1 Problem Statement
General-purpose horizontal classifieds platforms (e.g., OLX, Quikr, Facebook Marketplace) expose sellers to spam, off-platform UPI QR payment scams, and inadvertent personal data leakage when photos of textbooks, electronics, or hostel desks capture background ID cards, faces, or printed phone numbers. Furthermore, existing platforms offer either no pricing guidance or uncalibrated black-box point estimates without intervals or visual explanations.

### 1.2 Thesis & Contributions
Our thesis is that **human-in-the-loop, explainable, privacy-by-default AI lowers listing friction while preserving user agency and auditability**. Specifically, this work makes five contributions:
1. **Human-in-the-Loop Active Learning with Anti-Poisoning & Gated Promotion (Phase 15):** An eligibility-filtered correction stream from seller overrides evaluated against random and uncertainty sampling across 5 seeds and 10%/20% label-noise regimes (`ml/reports/active_learning/report.md`).
2. **Browser-First Photo Quality & Privacy Scrubber (Phase 7):** Client-side canvas redaction backed by `/scrub-verify`, evaluated on recall-first PII redaction and on-device vs. server latency/bandwidth trade-offs (`ml/reports/ondevice_vs_server/benchmark_report.md`).
3. **Explainable Condition Grading & Split-Conformal Price Estimation (Phases 8–10):** Monotonic ordinal condition scoring with Grad-CAM overlays (`ml/model_cards/condition_grader.md`) and split-conformal price intervals with plain-language top-3 SHAP reasons (`ml/model_cards/price_estimator.md`).
4. **Multilingual Hinglish Semantic Discovery & Algorithmic Multi-Party Swaps (Phases 12 & 16):** Rule-augmented 384-d semantic search outperforming Postgres FTS on code-mixed Hinglish queries (`NDCG@10 = 0.9852` vs. `0.8400`), paired with an algorithmic CP-SAT vertex-disjoint $\le 3$-cycle barter engine and cited LCA impact ranges (`docs/IMPACT_METHOD.md`).
5. **Agent-Based Marketplace Simulation & Reproducible User-Study Pipeline (Phases 17 & 18):** Multi-scale synthetic evaluation ($N = 100 \rightarrow 10,000$) with $\pm 50\%$ behavioural sensitivity analysis (`ml/reports/simulator/report.md`), Positioned strictly as synthetic supporting evidence (`data_origin='simulated'`), alongside a pre-registered paired $t$-test / Wilcoxon analysis pipeline (`ml/reports/user_study/report.md`).

---

## 2. Related Work

- **Online Secondhand Marketplaces & Trust:** Prior studies on peer-to-peer circular marketplaces highlight information asymmetry ("market for lemons") and safety risks during physical handovers. LOOP addresses this via community join-code/domain verification, dual-confirmed QR/OTP handovers, and an additive, transparent trust score formula (`ML_SPEC.md` §8).
- **Visual Privacy Scrubbing:** Unlike server-only redaction pipelines that transmit raw PII over the network, LOOP executes canvas pixelation client-side prior to upload and strictly avoids copyleft AGPL detectors (such as Ultralytics YOLOv8), relying exclusively on permissively licensed detectors and Indian phone/PIN OCR regexes.
- **Ordinal Grading & Conformal Valuation:** Standard cross-entropy classifiers ignore ordinal distance between condition grades (`poor < fair < good < like_new`). Conditional expected-value grading and split-conformal quantile regression provide distribution-free finite-sample interval coverage guarantees.

---

## 3. System Architecture

LOOP is architected as a modular monorepo (`apps/web` Next.js 15 PWA, `apps/api` FastAPI Python 3.11 service, `ml/` evaluation and runtime engines, and `sim/` discrete-time agent simulator) backed by PostgreSQL with `PostGIS` and `pgvector` (HNSW indexing) and Row Level Security (`RLS`) across all 9 Alembic migrations (`0001` through `0009`). Location privacy is enforced at the database schema level: no exact street address or raw GPS coordinate columns exist on identity tables (`geohash5` precision $\le 5$, verified by `test_schema_privacy.py`).

---

## 4. Methods

1. **On-Device Quality & Privacy Scrubber (`ml/src/quality_checker.py`, `ml/src/privacy_scrubber.py`):** Computes variance of Laplacian sharpness and mean luminance, detects 5 sensitive PII categories (`face`, `id_card`, `plate`, `phone`, `address`), applies irreversible client-side canvas pixelation, and blocks unscrubbed publishing at the server (`LISTING_NOT_SCRUBBED` guard + `/scrub-verify`).
2. **Product Recognition, Ordinal Condition & Conformal Pricing (`ml/src/product_recognition.py`, `ml/src/condition_grader.py`, `ml/src/price_estimator.py`):** Aggregates multi-photo features into 4 categories and subtypes (`T_cat` confidence threshold triggering top-3 user confirmation), computes ordinal condition probabilities $p_0..p_3$ with Grad-CAM saliency coordinates, and calibrates $q_{0.10}, q_{0.50}, q_{0.90}$ price intervals via split-conformal residuals to guarantee $\ge 80\%$ coverage.
3. **Human-in-the-Loop Active Learning (`ml/src/active_learning/retrain.py`):** Filters seller edits via anti-poisoning rules (verified user with $\ge 1$ completed trade + price within $0.2\times..3.0\times$ category/subtype median + conflicting-correction deduplication), checks SHA-256 hashes against `ml/data/manifests/frozen_test_hashes.json` to prevent test leakage, and promotes a retrained candidate **only if** it beats the active model on the primary metric without class regression.
4. **Algorithmic Swap Solver & Cited LCA Impact (`ml/src/swap_engine.py`, `ml/src/impact_estimator.py`):** Enumerates directed cycles of length $k \in \{2, 3\}$ within per-edge value tolerance $\delta = 0.30$ and solves vertex-disjoint set packing (`cpsat_set_packing_v1`), unlocking handovers only after all participants confirm. Environmental impact multiplies cited embodied $\text{CO}_2\text{e}$ (`ml/data/impact_factors.csv`) by displacement factor $d \in [0.30, 0.80]$.

---

## 5. Experiments & Ablation Results

### 5.1 Core Model Benchmarks vs. Baselines (Frozen Test Sets, `data_origin='simulated'`)

| Module | Baseline Metric | Improved LOOP Model Metric | Primary Gain | Logged Source |
| :--- | :--- | :--- | :--- | :--- |
| **Product Recognition** | Zero-shot: `84.2%` Top-1 (`0.831` F1) | Linear Probe + Multi-Photo: **`92.6%` Top-1** (`0.918` F1, `ECE = 0.031`) | `+8.4%` Top-1 | `ml/model_cards/product_recognition.md` |
| **Condition Grader** | Flat Cross-Entropy: `QWK = 0.684`, `MAE = 0.34` | Ordinal Expected-Value: **`QWK = 0.812`**, `MAE = 0.21` | `+0.128` QWK | `ml/model_cards/condition_grader.md` |
| **Price Estimator** | Category Median: `MAE = ₹310`, `MAPE = 28.5%` | Conformal Quantile + SHAP: **`MAE = ₹142`**, **`MAPE = 14.2%`**, **`81.4%` coverage** | `-14.3%` MAPE | `ml/model_cards/price_estimator.md` |
| **Semantic Search (Hinglish)** | Postgres FTS: `NDCG@10 = 0.8400`, `Recall@5 = 0.80` | Multilingual 384-d + Parser: **`NDCG@10 = 0.9852`**, **`Recall@5 = 1.00`** | `+0.1452` NDCG | `ml/reports/semantic_search/report.md` |
| **Active Learning (400 corr.)** | Static 20% Seed: `Top-1 = 0.7854`, `MAPE = 22.42%` | Seller Correction Stream (5 seeds): **`Top-1 = 0.9163 ± 0.0052`**, **`MAPE = 14.87% ± 0.14%`** | `+13.09%` Top-1 | `ml/reports/active_learning/report.md` |

### 5.2 System-Wide Ablation Study (`ml/reports/ablations/report.md`)
Removing semantic search degrades Hinglish `NDCG@10` by `-14.7%`; removing the on-device scrubber increases PII leak rate on sensitive images from `1.8%` to `100.0%`; removing active-learning updates leaves recognition accuracy at the `78.54%` cold-start seed level instead of `91.63%`.

---

## 6. User Study Protocol & Statistical Power Analysis (`ml/reports/user_study/report.md`)

- **Live Human Participant Measurements ($N = 30..50$ students):** `TBD (not yet measured on live participants; scheduled post-ethics clearance)`.
- **Reproducible Statistical Pipeline Verification (`data_origin='simulated'`, $N=40$ synthetic student profiles, `seed=42`):**
  - **Listing Time:** `45.3s` (with Snap-to-List AI) vs. `146.4s` (manual entry), paired $t = -26.835$ ($p < 10^{-12}$, Wilcoxon $z = -5.511$, Cohen's $d = -4.243$).
  - **Explanation Trust (1–7 Likert):** `5.92 / 7.0` (with Grad-CAM + SHAP + conformal intervals) vs. `4.27 / 7.0` (unexplained black-box), paired $t = 12.637$ ($p < 10^{-12}$, Cohen's $d = 1.998$).
  - **System Usability Scale (SUS):** `82.1 ± 6.0` (exceeding the `68.0` usability benchmark).

---

## 7. Marketplace Simulation & Sensitivity Analysis (`ml/reports/simulator/report.md`)

> **Synthetic Attribution:** All simulator outputs carry `data_origin='simulated'` and hold *under simulated behavioural assumptions*.

1. **Swap Scaling ($N = 100 \rightarrow 10,000$ Users):** Allowing 3-way cycles via CP-SAT set packing increases matched barter participants by **`+45.2%`** over the greedy 2-way baseline (`2,135` vs. `1,470` matched users at $N = 10,000$) while solving in `< 500 ms`.
2. **Trust Score & Fake-Review Ring Resilience:** The handover-gated trust formula achieves **`ROC-AUC = 0.9963`** separating honest traders from scammers and maintains **`ROC-AUC = 0.9963`** even under $2\times$ colluding fake-review ring intensity.
3. **Price-Drop Heuristic:** The floor-and-step-bounded hazard heuristic ($\text{floor} \ge 0.60\times\text{low}$, $\text{step} \le 15\%$) reduces simulated median time-to-sale from `18.4` days (`no_drop`) to `9.8` days while preserving an `0.89` revenue ratio.
4. **$\pm 50\%$ Sensitivity Analysis:** Across `0.5x`, `1.0x`, and `1.5x` behavioural perturbations, trust-score separation (`AUC >= 0.99`) and 3-way swap gains (`+45%`) remain invariant.

---

## 8. Discussion

Combining client-side privacy redaction with editable, uncertainty-aware AI predictions resolves the core tension between automation speed and user control. Importantly, clearly separating **machine learning models** (recognition, ordinal condition, conformal pricing, semantic embeddings) from **algorithmic/rule-based components** (CP-SAT swap cycles, LCA impact ranges, additive trust score, hazard price-drop heuristic) prevents over-claiming and improves user comprehension.

---

## 9. Limitations

1. **Synthetic & Simulated Evaluation (`data_origin='simulated'`):** The active learning curves, 50-query search corpus, fraud/scam benchmarks, and 10,000-agent simulator use synthetic/simulated datasets. Real-world campus distributions may exhibit higher noise and tail skew.
2. **Live Human User Study Pending (`TBD`):** While the within-subjects statistical pipeline (`paired t-test`, `Wilcoxon`, `SUS`) is implemented and verified on a synthetic power cohort, live human measurements require physical student sessions.
3. **Circularity in Simulated Price-Drop Evaluation:** In Phase 17, buyer willingness-to-pay in the simulator and the hazard price-drop heuristic share structural demand assumptions; real conversion gains must be validated in live pilot trading.
4. **Visual Condition Inspection Ceiling:** Surface photos cannot detect internal electronic faults (e.g., degraded laptop battery health or dead calculator keys); the UI explicitly discloses this limitation next to the Grad-CAM overlay.

---

## 10. Conclusion & Future Work

LOOP demonstrates a complete, privacy-preserving, human-in-the-loop AI marketplace for campus reuse that runs entirely on CPU/browser runtimes with permissive open-source dependencies. Future work includes executing the 50-student live campus pilot study, collecting multi-annotator real-world photo datasets under Phase 2 ethics clearance, and extending the CP-SAT barter solver to asynchronous rolling time windows.

---

## Appendix: Claim-Audit & Reproducibility Checklist (`PAPER_PLAN.md` §5 & §9)

- [x] Code and configs prepared for tag `paper-v1`
- [x] Deterministic seeds (`[42, 101, 202, 303, 404]`) and frozen test-set hashes (`ml/data/manifests/frozen_test_hashes.json`) verified
- [x] Model cards completed for all 6 ML/detection modules (`ml/model_cards/*.md`)
- [x] Master script `ml/reports/make_figures.py` regenerates all 8 figures/manifests (`ml/reports/figure_manifest.json`)
- [x] Paired $t$-test, Wilcoxon signed-rank test, Cohen's $d$, and 95% CIs implemented (`ml/src/eval_user_study_and_ablations.py`)
- [x] Unmeasured live human metrics explicitly marked `TBD (not yet measured on live participants)`
