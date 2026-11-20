# Semantic Multilingual Search Evaluation Report (50-Query Set)

> **Date:** October 2026  
> **Scope:** Phase 12 — Semantic Multilingual Search (384-d) vs FTS Baseline  
> **Dataset:** 50-query campus benchmark (25 English + 25 Hinglish)

---

## 1. Evaluation Results

| Subset | Method | Recall@5 | Recall@10 | NDCG@10 | MRR | Mean Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **English (25)** | **Semantic (384-d + Parser)** | 1.0000 | 1.0000 | 0.9557 | 0.9400 | 1.873 |
| **English (25)** | FTS Baseline | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.008 |
| **Hinglish (25)** | **Semantic (384-d + Parser)** | **1.0000** | **1.0000** | **0.9852** | **0.9800** | 1.817 |
| **Hinglish (25)** | FTS Baseline | 0.8800 | 0.8800 | 0.8400 | 0.8267 | 0.008 |

---

## 2. Key Findings

1. **Hinglish Superiority:** On code-mixed Hinglish queries (e.g., *"padhai ki mez 3000 ke andar Wakad ke paas"*, *"engineering ki kitab"*), Semantic Search outperforms FTS by **+14.5% NDCG@10** and **+12.0% Recall@5** because FTS fails when Hindi/Hinglish terms (`kitab`, `mez`, `kursi`, `gadda`) do not appear verbatim in English listing titles.
2. **Structured Constraint Parsing:** Queries containing price ceilings (`under 3000`, `3000 ke andar`) and coarse place names (`near Wakad`, `Wakad ke paas`) are parsed into SQL `price_max` and `area_name` filters before vector ranking.
3. **Latency:** Mean query encoding + cosine ranking latency is **< 2 ms** per query.
