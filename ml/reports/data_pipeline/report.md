# Phase 2: Data Collection, Deduplication & Stratified Split Report

> **Data Origin Notice (`AGENTS.md` §2):** Pipeline verification statistics below run on deterministic synthetic listing records (`data_origin='simulated'`). Live campus volunteer photo counts are marked `TBD (parallel human collection track)`.

## 1. Perceptual-Hash Deduplication & Stratified Split (`70 / 15 / 15`)

- **Manifest SHA-256 Digest:** `82ad16bea6609edac8b8545be6c791622e9b87aa77feba29eaab22e9b5337a1b`
- **Total Input Photos:** `111`
- **Accepted Photos (after `Hamming <= 6` phash deduplication):** `107`
- **Near-Duplicates Filtered (`Hamming <= 6`):** `4`
- **Unique Multi-Photo Listings:** `80`
- **Split Breakdown:**
  - `train`: `61` photos
  - `val`: `22` photos
  - `test` (frozen): `24` photos
- **Cross-Split Leakage Audit:**
  - Zero `listing_id` overlap across splits: **`True`**
  - Zero near-duplicate (`Hamming <= 6`) across splits: **`True`**

## 2. Multi-Annotator Condition Agreement (`ML_SPEC.md` §§1, 3)

- **Quadratic Weighted Cohen's Kappa ($\kappa_w$):** **`0.9507`**
- **Linear Weighted Cohen's Kappa:** **`0.9021`**
- **Tie-Breaker Protocol:** 3rd annotator resolves disagreements (`docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md` §3).

## 3. Category & Condition Distribution (`data_origin='simulated'`)

- **Categories:** `{"electronics": 27, "furniture": 26, "books": 27, "hobbies": 27}`
- **Ordinal Condition Grades:** `{"poor": 27, "fair": 26, "good": 27, "like_new": 27}`
- **50-Query Search Set (`ml/data/templates/search_queries_50_en_hinglish.json`):** `25` English + `25` Hinglish queries.
