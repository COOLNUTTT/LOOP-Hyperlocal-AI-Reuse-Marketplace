# DEMO_SCRIPT: LOOP Evaluator Walkthrough & Platform Comparison

> **Target Duration:** 8–10 minutes  
> **Seeded Command:** `python scripts/seed.py` (`data_origin='simulated'`)

---

## 1. Evaluator Demo Accounts (Synthetic Seed Data)

| Role | Email | Community | Verified | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Seller (Student A)** | `seller.demo@adypu.edu.in` | ADYPU Lohegaon Campus | Yes (`tek3x`) | Demonstrate Snap-to-List, Scrubber, Corrections & Price-Drop |
| **Buyer (Student B)** | `buyer.demo@adypu.edu.in` | ADYPU Lohegaon Campus | Yes (`tek3x`) | Demonstrate Hinglish Search, Fair-Deal Badge, Chat & OTP Handover |
| **Moderator / Admin** | `admin.demo@adypu.edu.in` | ADYPU Lohegaon Campus | Yes (`admin`) | Demonstrate Flag Queue, Audit Logs & Active-Learning Gated Promotion |

---

## 2. Step-by-Step Live Walkthrough

1. **Step 1 — Privacy-First Snap-to-List (`/sell`):**
   - Upload an item photo containing a phone number or ID card.
   - Show the **On-Device Quality Check** (Laplacian blur + luminance) and the **Interactive Canvas Privacy Scrubber** redacting PII before upload (plus `/scrub-verify` server safeguard).
   - Review the **AI Draft**: Category (`top-3` + confidence), **Ordinal Condition Grade** with toggleable **Grad-CAM heatmap overlay**, and **80% Split-Conformal Price Range** with plain-language **SHAP top-3 reasons**.
   - Edit one AI field (e.g., condition or price) and publish — showing that an active-learning `corrections` row is logged automatically.
2. **Step 2 — Multilingual Hinglish Discovery & Fair-Deal Badge (`/browse`, `/listings/[id]`):**
   - Search `"sasta study table under 3000 near Wakad"` or `"casio calculator"`.
   - Show coarse geohash privacy (`geohash5`, area centroids only — no exact street address).
   - Open the listing detail page to inspect the **Fair-Deal Badge**, **SHAP price factors**, and the **Dynamic Price-Drop Suggestion Card** (labelled *Algorithmic Hazard Heuristic*, bounded by floor $\ge 0.60\times\text{low}$ and step $\le 15\%$).
3. **Step 3 — Safe Chat, Scam Warning & Dual-Confirmed OTP Handover (`/chat`):**
   - Send a message containing `"scan QR code for advance payment"` to trigger the real-time **Chat-Safety Warning** and negotiation hint.
   - Generate a short-lived handover OTP and confirm from both buyer and seller to unlock **Gated Reviews** and the **Additive Trust Score Breakdown**.
4. **Step 4 — Algorithmic 3-Way Swap & Cited Impact Dashboard (`/swap`, `/impact`):**
   - Add a wishlist item on `/swap` and inspect a matched **3-Way Disjoint Swap Cycle** (labelled *Algorithmic CP-SAT Graph Solver — Not ML*), confirming all 3 edges to unlock per-edge handovers.
   - Open `/impact` to show avoided $\text{CO}_2\text{e}$ and e-waste ranges ($d \in [0.30, 0.80]$) and the 5-point sensitivity table traced to [`ml/data/impact_factors.csv`](../ml/data/impact_factors.csv).
5. **Step 5 — Human-in-the-Loop Moderation & Active Learning Governance (`/admin`):**
   - Review flagged listings (never auto-removed), execute a moderator action writing an immutable `audit_logs` row, and trigger **Gated Model Promotion / Rollback** on the frozen test set.

---

## 3. Honest Comparison with Existing Classifieds Platforms

| Capability | OLX India | Quikr | Facebook Marketplace | LOOP (This Work) |
| :--- | :--- | :--- | :--- | :--- |
| **Client-Side PII Scrubber (Faces/IDs/Plates/Phones)** | No | No | No | **Yes** (Browser canvas + `/scrub-verify`) |
| **Explainable Condition Grading (Grad-CAM Saliency)** | No | No | No | **Yes** (Ordinal expected-value + dismissible Grad-CAM) |
| **Calibrated Price Intervals + Plain-Language SHAP** | Point / tier suggestion | Broad range | No public SHAP | **Yes** (80% Split-Conformal + top-3 SHAP reasons) |
| **Human-in-the-Loop Active Learning from Seller Edits** | Proprietary / undisclosed | No | Proprietary | **Yes** (Anti-poisoning filter + frozen test-set gate) |
| **Multi-Party ($\le 3$-Way) Disjoint Barter Swap Solver** | No (1-to-1 chat only) | No | No | **Yes** (Algorithmic CP-SAT cycle packing + all-party confirm) |
| **Coarse-Only Location by Default (`geohash5` $\le 5$)** | Approximate area | Approximate area | Approximate area | **Yes** (Schema-enforced deny-list on exact address columns) |
| **Cited Range-Based LCA Impact + Sensitivity Table** | No | No | No | **Yes** (`ml/data/impact_factors.csv`, $d \in [0.30, 0.80]$) |
