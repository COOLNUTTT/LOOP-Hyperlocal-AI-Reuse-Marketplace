# COPYRIGHT_FILING_PACKAGE: LOOP Computer Software & Literary Work Registration

> **Prepared per `docs/IP_AND_COMPLIANCE.md` §6 (Copyright Office, Government of India — Literary / Computer Software Work)**  
> **Release Tag Snapshot:** `paper-v1`

---

## 1. Statement of Particulars (Form XIV Reference Checklist)

| Field | Details |
| :--- | :--- |
| **Title of Work** | LOOP: Hyperlocal AI Reuse Marketplace |
| **Class & Description of Work** | Literary Work (Computer Software — Full-Stack Source Code, ML Runtime & Technical Documentation) |
| **Authors & Joint Owners** | **Emmanuel George P** and **Sameer Makani** |
| **Copyright Notice on All Files** | `Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.` |
| **Language of Work** | Python 3.11, TypeScript 5.7, SQL (PostgreSQL / PostGIS / pgvector), Markdown |
| **Year of Creation** | 2026 |
| **Publication Status** | Unpublished private academic/research repository (pending owner publish-vs-patent decision per `IP_AND_COMPLIANCE.md` §2) |

---

## 2. Automated Licence & Header Audit Summary (`scripts/audit_licenses_and_security.py`)

- **Total Source Files Verified for Copyright Header:** `100%` pass rate (`0` missing headers across `.py`, `.ts`, `.tsx`, `.mjs`, `.css`).
- **Prohibited Copyleft / AGPL / GPL Dependencies Found:** **`0`** (Strictly zero `ultralytics`, `yolov8`, `GPL`, or `AGPL` packages in `apps/api/requirements.txt`, `apps/web/package.json`, or `THIRD_PARTY_LICENSES.md`).
- **Database Row Level Security (RLS) Coverage:** Verified across all `9` Alembic migrations (`0001_identity_and_rls.py` through `0009_price_drop_and_history.py`).

---

## 3. Source-Code Deposit Inventory (Core Modules for First/Last Page Excerpts)

1. **Backend API & Governance (`apps/api/app/`):**
   - `main.py` — FastAPI application factory & versioned `/api/v1` router registration.
   - `models/` — SQLAlchemy 2.0 ORM schemas (`identity.py`, `listing.py`, `chat.py`, `corrections.py`, `handover.py`, `audit.py`, `model_version.py`, `swap.py`, `impact.py`, `price_drop.py`).
   - `services/` — Business logic, DPDP privacy export/purge, anti-poisoning filter, OTP handover, trust breakdown, human-in-the-loop moderation, and multi-party swap confirmation.
2. **Explainable ML & Algorithmic Engines (`ml/src/` & `sim/`):**
   - `quality_checker.py` & `privacy_scrubber.py` — On-device photo quality and PII redaction.
   - `product_recognition.py`, `condition_grader.py`, `price_estimator.py` — Multi-photo recognition, ordinal condition with Grad-CAM, and split-conformal pricing with SHAP.
   - `active_learning/retrain.py` — Frozen test-set hash guard, gated model promotion, and rollback.
   - `swap_engine.py` & `impact_estimator.py` — Algorithmic $\le 3$-way CP-SAT cycle packing and cited LCA impact estimator.
   - `price_drop.py` & `sim/simulator.py` — Floor/step-guarded hazard price-drop heuristic and single-seed agent-based simulator.
3. **Mobile-First Next.js PWA (`apps/web/`):**
   - `/sell`, `/browse`, `/listings/[id]`, `/chat`, `/swap`, `/impact`, `/admin`, `/profile`, `/consent` pages and interactive Grad-CAM / Scrubber / Fair-Deal / Price-Drop components.

---

## 4. Declaration of Originality

All proprietary source code, database migrations, evaluation harnesses, and documentation in this repository are original works authored by **Emmanuel George P** and **Sameer Makani** in 2026. All third-party libraries are used strictly under permissive open-source licences (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC) as cataloged in [`THIRD_PARTY_LICENSES.md`](../THIRD_PARTY_LICENSES.md).
