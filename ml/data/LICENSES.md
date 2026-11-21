# LOOP Dataset & Environmental Factor Licences (`ml/data/LICENSES.md`)

All datasets and lookup tables used in LOOP adhere strictly to permissive or first-party terms (`CC0-1.0`, `CC-BY-4.0`, `MIT`, `Apache-2.0`, or first-party proprietary under DPDP Act 2023 volunteer consent) per `docs/IP_AND_COMPLIANCE.md` §4 and `AGENTS.md` §2.

| Dataset / Asset | Path | Origin (`data_origin`) | Licence | Redistribution / Privacy Rule |
| :--- | :--- | :--- | :--- | :--- |
| **`LOOP-Images` (Synthetic Pipeline Set)** | `ml/data/manifests/` | `simulated` | First-Party (`All rights reserved`) | Synthetic verification metadata; zero personal data. |
| **`LOOP-Images` (Pilot Volunteer Photos)** | Offline / Supabase Storage (`loop-dev`) | `user` | First-Party (`DPDP Consent`) | Not committed to git; governed by `docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md`. |
| **`LOOP-Price` (Campus Price Observations)** | `ml/data/templates/local_price_observations_template.csv` | `simulated` / `user` | First-Party (`CC0-1.0` schema) | Stores only tabular price, category, subtype, brand, condition, and age; zero copied external images or PII. |
| **`LOOP-Search` (50 EN + Hinglish Queries)** | `ml/data/templates/search_queries_50_en_hinglish.json` | `simulated` / `first_party` | First-Party (`All rights reserved`) | 25 English + 25 Hinglish hand-authored campus search queries. |
| **`LOOP-Scrub` (Staged Privacy Set)** | `ml/data/templates/staged_scrub_annotations_template.csv` | `simulated` / `user` | First-Party (`DPDP Staged Consent`) | Only consenting volunteers + mock IDs, mock plates (`MH 12 AB 0000`), and dummy phone numbers. |
| **`LOOP-Scam` (Chat & Listing Scam Corpus)** | `ml/src/eval_fraud.py` | `simulated` | First-Party (`All rights reserved`) | Explicitly flagged `data_origin='simulated'`. |
| **`LOOP-Impact` (Embodied Carbon Factors)** | `ml/data/impact_factors.csv` | `cited_lca` | Public LCA Facts (`Apple PER`, `Dell PCF`, `ADEME`, `WRAP UK`) | Cited numerical emission constants with year and source attribution (`docs/IMPACT_METHOD.md`). |
