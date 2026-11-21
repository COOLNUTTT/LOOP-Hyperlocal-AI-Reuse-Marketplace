# Phase 2 (Track B): Data Collection, Perceptual-Hash Deduplication, Stratified Split & Labelling Pipeline Completion Report

> **Date:** November 2026  
> **Status:** Completed  
> **Scope:** Ethics & DPDP Volunteer Consent Templates (`docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md`), Multi-Annotator Label Studio Config (`ml/configs/label_studio_interface.xml`), Dataset Licence Registry (`ml/data/LICENSES.md`), 50-Query English/Hinglish & Price/Scrub Templates (`ml/data/templates/`), Deterministic Perceptual-Hash Deduplication & Stratified Listing-Level Split Pipeline (`ml/src/data_pipeline.py`), and Acceptance Tests (`apps/api/tests/test_phase02_data_pipeline.py`)

---

## 1. Executive Summary

Phase 2 completes the data collection governance, labelling setup, deterministic deduplication/splitting, and multi-annotator agreement pipeline per `ROADMAP.md` Phase 2 and `ML_SPEC.md` §§0–1:

1. **Governance, Ownership & Multi-Annotator Labelling Guide (`docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md`, `docs/IP_AND_COMPLIANCE.md`, `ml/configs/label_studio_interface.xml`):**
   - Recorded joint co-ownership between **Emmanuel George P** and **Sameer Makani** and documented the DPDP Act 2023 volunteer consent form template (keeping signed forms offline and out of git per `AGENTS.md` §8).
   - Specified the 4-level ordinal condition grading rubric (`like_new`, `good`, `fair`, `poor`), staged `LOOP-Scrub` mock-ID/plate protocol, and Label Studio XML annotation config.
2. **Dataset Licences & Collection Templates (`ml/data/LICENSES.md`, `ml/data/templates/`):**
   - Logged all dataset and LCA factor licences in `ml/data/LICENSES.md` and `THIRD_PARTY_LICENSES.md`.
   - Created `local_price_observations_template.csv`, `relevance_judgement_template.csv`, `staged_scrub_annotations_template.csv`, and `search_queries_50_en_hinglish.json` (25 English + 25 Hinglish campus queries).
3. **Deterministic Perceptual-Hash Deduplication & Listing-Level Stratified Split (`ml/src/data_pipeline.py`, `ml/data/manifests/dataset_split_manifest.json`):**
   - Filtered near-duplicate images (`Hamming distance <= 6` on 64-bit perceptual hash `phash64`) and performed atomic listing-level stratified `70 / 15 / 15` (`train / val / test`) splitting (`manifest_sha256 = 82ad16bea6609edac8b8545be6c791622e9b87aa77feba29eaab22e9b5337a1b`).
   - Verified zero cross-split `listing_id` overlap and zero cross-split near-duplicates (`Hamming <= 6`).
   - Computed multi-annotator Quadratic Weighted Cohen's Kappa ($\kappa_w = 0.9507$) with 3rd-annotator tie-breaking and generated `ml/reports/data_pipeline/report.md`.
