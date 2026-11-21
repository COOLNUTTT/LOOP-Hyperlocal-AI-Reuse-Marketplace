# IMPACT_METHOD: Algorithmic Reuse Impact Estimation Methodology

> **Honesty Disclosure (AGENTS.md §2.3):** The LOOP environmental impact estimator is an **algorithmic lookup and sensitivity model**, not a machine learning model. It reports conservative-to-optimistic intervals rather than false single-point precision.

---

## 1. Mathematical Formulation

For each completed secondhand handover $i$ in category $c_i$ and subtype $s_i$:

$$\Delta \text{CO}_2\text{e}_i(d) = E_{\text{embodied}}(c_i, s_i) \times d$$

$$\Delta M_i(d) = W_{\text{mass}}(c_i, s_i) \times d$$

where:
- $E_{\text{embodied}}(c_i, s_i)$ is the cradle-to-gate embodied greenhouse gas emissions ($\text{kg CO}_2\text{e}$) of manufacturing a new equivalent product from the cited factor table [`ml/data/impact_factors.csv`](../ml/data/impact_factors.csv).
- $W_{\text{mass}}(c_i, s_i)$ is the physical mass ($\text{kg}$) of the product diverted from premature disposal or e-waste streams.
- $d \in [0.30, 0.80]$ is the **reuse displacement factor** (the probability that a local peer-to-peer reuse transaction displaces the manufacture and purchase of a brand-new retail unit, rather than inducing secondary consumption).

We report:
- **Conservative Lower Bound ($d = 0.30$):** Assumes only 30% of campus secondhand trades replace a brand-new purchase.
- **Central Reference ($d = 0.55$):** Mid-range displacement rate observed in empirical circular-economy literature.
- **Upper Bound ($d = 0.80$):** High-substitution regime typical for mandatory campus textbooks, calculators, and hostel study desks.

---

## 2. Cited Factor Table Summary (`ml/data/impact_factors.csv`)

| Category | Subtype | Embodied $\text{CO}_2\text{e}$ (kg) | Mass (kg) | Cited Source | Year |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `electronics` | `laptop` | 210.0 | 1.80 | Dell & Apple Product Environmental Reports (14-inch Laptop LCA Median) | 2024 |
| `electronics` | `smartphone` | 65.0 | 0.19 | Apple iPhone & Fairphone Life Cycle Assessment Reports | 2024 |
| `electronics` | `monitor` | 185.0 | 4.50 | Dell 24-inch LCD Monitor Product Carbon Footprint Report | 2023 |
| `electronics` | `scientific calculator` | 12.5 | 0.15 | ADEME Base Empreinte Small Consumer Electronics LCA | 2023 |
| `furniture` | `study table` | 45.0 | 14.50 | FIRA Furniture Industry Research Association Desk Carbon Footprint Study | 2022 |
| `furniture` | `office chair` | 62.0 | 12.00 | FIRA Task Chair Life Cycle Assessment Report | 2022 |
| `books` | `textbook` | 4.2 | 0.85 | Book Industry Study Group & Carbon Trust Paper Publishing LCA | 2022 |
| `hobbies` | `bicycle` | 135.0 | 13.50 | Trek & European Cyclists Federation Aluminum Commuter Bicycle LCA | 2023 |

---

## 3. Sensitivity Analysis Protocol

Because the true displacement factor $d$ cannot be directly observed without counterfactual buyer surveys, every impact report (both personal `/impact/me` and community `/impact/community`) includes a sensitivity table over:

$$d \in \{0.30, 0.45, 0.55, 0.70, 0.80\}$$

Local hyperlocal handovers within a campus or hostel occur on foot, so last-mile motorised shipping emissions are zero in the baseline model.
