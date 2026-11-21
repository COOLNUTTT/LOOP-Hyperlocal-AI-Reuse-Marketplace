# Phase 18: User Study Protocol & Reproducible Statistical Analysis Report

> **Live Human Study Status (AGENTS.md §8 Honesty Rule):** `TBD (not yet measured on live participants)`  
> **Pipeline Verification Dataset:** `Simulated Power-Analysis Cohort (data_origin='simulated', N=40, seed=42)`  
> **Figure:** `ml/reports/user_study/user_study_figure_synthetic.svg`

---

## 1. Ethics, Consent & Study Protocol (30–50 Campus Students)

1. **Consent & Privacy:** All human sessions require written informed consent under DPDP Act 2023 guidelines (`/consent` screen + offline consent log stored separately from anonymised CSVs). No PII or raw participant photos are stored.
2. **Within-Subjects Tasks (Counterbalanced Order):**
   - **Task A (Listing Creation):** List 2 campus items — one with **Snap-to-List AI** and one with **Manual Form Entry**.
   - **Task B (Explanation Trust Evaluation):** Evaluate condition & price recommendations **with explanations** (Grad-CAM saliency + plain-language SHAP + 80% conformal range) vs. **without explanations** (point estimate only).
   - **Task C (Discovery & Multi-Party Swap):** Search using Hinglish/English queries and confirm a 3-way swap proposal, followed by the 10-item System Usability Scale (SUS).

---

## 2. Measured Live Results vs. Simulated Power-Analysis Verification

| Measure | Live Human Study ($N=30..50$) | Simulated Power-Analysis Cohort ($N=40$, `simulated`) | Paired $t$-Stat (`simulated`) | Wilcoxon $z$ (`simulated`) | Effect Size Cohen's $d$ (`simulated`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Listing Time (With AI vs. Manual)** | `TBD (not yet measured)` | `47.2s` vs. `153.1s` ($\Delta = -105.9\text{s}$) | `-30.869` ($p = 1e-12$) | `-5.511` | `-4.881` |
| **Trust (1–7, With vs. Without Explanations)** | `TBD (not yet measured)` | `5.86` vs. `4.33` ($\Delta = +1.53$) | `9.999` ($p = 1e-12$) | `5.484` | `1.581` |
| **System Usability Scale (SUS 0–100)** | `TBD (not yet measured)` | `82.8 ± 5.0` (Industry threshold: `68.0`) | — | — | — |
