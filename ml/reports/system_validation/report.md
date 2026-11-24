# Phase 18: End-to-End System Validation & Load Benchmark Report

> **Data Origin:** `simulated` (`data_origin='simulated'`)  
> **Iterations:** `50` full analyze + search pipeline executions

---

## 1. End-to-End Core User Journeys

| Journey | Scope Verified | Status |
| :--- | :--- | :--- |
| **1. Snap-to-List** | Quality check $\rightarrow$ Privacy scrubber $\rightarrow$ Recognition $\rightarrow$ Ordinal Condition $\rightarrow$ Conformal Price $\rightarrow$ Smart Autofill | `PASSED` |
| **2. Find & Buy** | Hinglish/English query parser $\rightarrow$ 384-d semantic embedding $\rightarrow$ Hazard price-drop guardrail check | `PASSED` |
| **3. Multi-Party Swap & Impact** | Wishlist compatibility graph $\rightarrow$ CP-SAT cycle packing $\rightarrow$ Cited LCA carbon range & sensitivity | `PASSED` |
| **4. Trust, Fraud & Moderation** | pHash/CLIP duplicate & scam-text classifier $\rightarrow$ Human moderator queue (no auto-removal) | `PASSED` |

---

## 2. Throughput & Latency Benchmark

- **p50 Pipeline Latency:** `0.116 ms`
- **p95 Pipeline Latency:** `0.191 ms` (Target: `< 1000.0 ms`)
- **Measured CPU Throughput:** `7804.0 pipelines/sec`
