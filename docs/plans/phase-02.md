# Phase 2 (Track B): Data Collection, Perceptual-Hash Deduplication, Stratified Split & Labelling Pipeline Plan

> **Goal:** Complete Phase 2 (`ROADMAP.md` §Phase 2, `ML_SPEC.md` §§0–1, `IP_AND_COMPLIANCE.md` §§1, 3, 4) by establishing the data governance templates, multi-annotator condition labelling guide + Label Studio config, dataset licence registry (`ml/data/LICENSES.md`), 50-query English/Hinglish search & relevance-judgement templates, and the deterministic ingestion, 64-bit perceptual-hash deduplication (`Hamming <= 6`), listing-level stratified `70/15/15` split, inter-annotator weighted Cohen's kappa calculator, and dataset statistics report generator (`ml/src/data_pipeline.py`).

---

## 1. Architecture & Non-Negotiable Constraints

1. **Ethics, Consent & Ownership Templates (`docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md`, `IP_AND_COMPLIANCE.md`):**
   - Document the university ethics exemption/clearance record template, joint authorship/ownership record between Emmanuel George P and Sameer Makani, DPDP Act 2023 volunteer photo consent template (blank template only — never commit signed participant forms or raw PII photos per `AGENTS.md` §8), and staged `LOOP-Scrub` protocol (strictly mock IDs, mock plates, and consenting volunteer faces).
   - Provide the 4-grade ordinal condition labelling rubric (`0: poor`, `1: fair`, `2: good`, `3: like_new`) across Electronics, Furniture, Books, and Hobbies, plus a Label Studio XML/JSON interface config (`ml/configs/label_studio_interface.xml`).

2. **Dataset Licences & Observation Templates (`ml/data/LICENSES.md`, `ml/data/templates/`):**
   - Create `ml/data/LICENSES.md` and update `THIRD_PARTY_LICENSES.md` logging dataset licences (`CC0-1.0`, `CC-BY-4.0`, and first-party `LOOP-*` datasets).
   - Create `ml/data/templates/local_price_observations_template.csv`, `ml/data/templates/relevance_judgement_template.csv`, `ml/data/templates/staged_scrub_annotations_template.csv`, and `ml/data/templates/search_queries_50_en_hinglish.json` (25 English + 25 Hinglish campus queries).

3. **Deterministic Data Pipeline (`ml/src/data_pipeline.py`):**
   - **Perceptual-Hash Deduplication:** Compute 64-bit perceptual hashes (`phash64`) and cluster/deduplicate near-identical images with Hamming distance $\le 6$ (`ML_SPEC.md` §0) so duplicates never leak across `train`, `val`, and `test`.
   - **Listing-Level Stratified Split (`70 / 15 / 15`):** Group multi-photo items by `listing_id` before stratified splitting by `(category, condition_grade)` using a fixed seed (`seed=42`) so photos from the same listing never straddle splits and running the split script twice yields the exact same manifest SHA-256 hash.
   - **Inter-Annotator Agreement:** Compute linear and quadratic weighted Cohen's $\kappa$ across $\ge 2$ annotators with tie-breaker resolution (`ML_SPEC.md` §1).
   - **Manifest & Statistics Report:** Output `ml/data/manifests/dataset_split_manifest.json` and `ml/reports/data_pipeline/report.md` (explicitly tagging synthetic verification records `data_origin='simulated'` and live pilot records `TBD` until volunteer uploads conclude).

4. **Acceptance Testing (`apps/api/tests/test_phase02_data_pipeline.py`):**
   - Verify deterministic splitting (two runs produce identical SHA-256 manifest hashes).
   - Verify zero near-duplicates (`Hamming <= 6`) across `train`, `val`, and `test`.
   - Verify zero `listing_id` overlap across splits.
   - Verify quadratic weighted Cohen's $\kappa$ calculation, 50-query English/Hinglish template completeness, `ml/data/LICENSES.md`, and copyright headers.

---

## 2. Task Breakdown

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p2-task-1 | Create `docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md`, `ml/configs/label_studio_interface.xml`, and update `IP_AND_COMPLIANCE.md` | completed | Ethics/DPDP consent template, condition rubric & staged scrub protocol |
| p2-task-2 | Create `ml/data/LICENSES.md` and templates in `ml/data/templates/` (price observations, 50 EN/Hinglish queries, relevance judgements, scrub boxes) | completed | Logged dataset licences in `ml/data/LICENSES.md` & `THIRD_PARTY_LICENSES.md` |
| p2-task-3 | Implement `ml/src/data_pipeline.py` (64-bit phash dedupe `Hamming <= 6`, listing-level stratified `70/15/15` split, weighted Cohen's kappa, stats report) | completed | Deterministic manifest hash + `ml/reports/data_pipeline/report.md` |
| p2-task-4 | Write `apps/api/tests/test_phase02_data_pipeline.py`, run full test/lint/licence audits, and write `docs/plans/phase-02-report.md` | completed | All Phase 2 acceptance checks in `ROADMAP.md` passed |
