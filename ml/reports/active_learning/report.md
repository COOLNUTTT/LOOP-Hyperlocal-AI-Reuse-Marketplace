# Phase 15: Active Learning Loop Evaluation Report (Simulated Corrections)

> **Data Origin:** `simulated` (`data_origin='simulated'`)
> **Seeds Evaluated:** `[42, 101, 202, 303, 404]` ($N=5$ seeds, reporting $\text{mean} \pm \text{std}$ error bands)
> **Initial Seed Training Split:** 20% of training data (`0` corrections)
> **Correction Batches:** `[0, 25, 50, 100, 200, 400]`
> **Figure:** `ml/reports/active_learning/active_learning_curves_synthetic.svg`

---

## 1. Headline Learning Curves (0% Label Noise — Simulated Corrections)

### 1.1 Product Recognition (Top-1 Accuracy, Higher is Better)

| Corrections | Random ($\text{mean} \pm \text{std}$) | Uncertainty ($\text{mean} \pm \text{std}$) | Correction Stream ($\text{mean} \pm \text{std}$) |
| :--- | :--- | :--- | :--- |
| 0 | 0.7850 ± 0.0029 | 0.7863 ± 0.0036 | 0.7822 ± 0.0031 |
| 50 | 0.8088 ± 0.0043 | 0.8213 ± 0.0056 | 0.8259 ± 0.0051 |
| 100 | 0.8232 ± 0.0065 | 0.8401 ± 0.0019 | 0.8491 ± 0.0066 |
| 200 | 0.8395 ± 0.0063 | 0.8774 ± 0.0062 | 0.8856 ± 0.0063 |
| 400 | 0.8540 ± 0.0044 | 0.8997 ± 0.0067 | 0.9181 ± 0.0041 |

### 1.2 Condition Grader (Quadratic Weighted Kappa — QWK, Higher is Better)

| Corrections | Random ($\text{mean} \pm \text{std}$) | Uncertainty ($\text{mean} \pm \text{std}$) | Correction Stream ($\text{mean} \pm \text{std}$) |
| :--- | :--- | :--- | :--- |
| 0 | 0.6420 ± 0.0035 | 0.6405 ± 0.0042 | 0.6433 ± 0.0037 |
| 100 | 0.6848 ± 0.0071 | 0.7150 ± 0.0011 | 0.7195 ± 0.0066 |
| 400 | 0.7315 ± 0.0049 | 0.7839 ± 0.0051 | 0.8003 ± 0.0099 |

### 1.3 Price Estimator (MAPE %, Lower is Better)

| Corrections | Random ($\text{mean} \pm \text{std}$) | Uncertainty ($\text{mean} \pm \text{std}$) | Correction Stream ($\text{mean} \pm \text{std}$) |
| :--- | :--- | :--- | :--- |
| 0 | 22.37% ± 0.18% | 22.38% ± 0.14% | 22.39% ± 0.25% |
| 100 | 20.35% ± 0.24% | 19.28% ± 0.25% | 18.53% ± 0.22% |
| 400 | 18.14% ± 0.26% | 15.58% ± 0.27% | 14.82% ± 0.13% |

---

## 2. Label-Noise Robustness (10% and 20% Simulated Correction Noise at 400 Corrections)

| Model & Metric | 0% Noise (Correction Stream) | 10% Label Noise (Correction Stream) | 20% Label Noise (Correction Stream) |
| :--- | :--- | :--- | :--- |
| Recognition (Top-1) | 0.9181 ± 0.0041 | 0.9040 ± 0.0067 | 0.8844 ± 0.0019 |
| Condition (QWK) | 0.8003 ± 0.0099 | 0.7837 ± 0.0067 | 0.7673 ± 0.0056 |
| Price (MAPE %) | 14.82% ± 0.13% | 15.94% ± 0.23% | 16.51% ± 0.31% |

---

## 3. Limitations & Honesty Disclosure

- **Simulated Corrections (`data_origin='simulated'`):** All curves and error bands in `active_learning_curves_synthetic.svg` and `learning_curves_synthetic.json` are generated from simulated corrections on synthetic pools.
- **Anti-Poisoning Mitigation:** Verification gating (`is_verified` + completed trade check) and $3\times$ median price bounds prevent unbounded corruption under 10% and 20% label noise, while gated promotion on the frozen test set guarantees that any candidate failing to beat the active model is rejected.
