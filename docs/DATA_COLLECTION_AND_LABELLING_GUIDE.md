# Data Collection Protocol, Consent Templates & Multi-Annotator Labelling Guide (Phase 2)

**Authors & Joint Owners:** Emmanuel George P and Sameer Makani  
**Compliance Scope:** `ROADMAP.md` Phase 2, `ML_SPEC.md` §§0–1, `IP_AND_COMPLIANCE.md` §§1, 3, 4, and India's Digital Personal Data Protection (DPDP) Act, 2023.

> **Git Security Rule (`AGENTS.md` §8):** This file contains **blank consent templates and annotation protocols only**. Signed participant consent forms, volunteer identity records, and raw unscrubbed photos showing people or real personal documents must **never** be committed to the repository.

---

## 1. Joint Ownership & Authorship Record (`IP_AND_COMPLIANCE.md` §1)

- **Rightsholders:** Emmanuel George P and Sameer Makani (Joint equal co-authors and co-owners).
- **Copyright Notice:** `Copyright (c) 2026 Emmanuel George P and Sameer Makani. All rights reserved.`
- **Pilot Community:** Ajeenkya D Y Patil University (ADYPU), Lohegaon / Charholi Budruk, Pune (`geohash5 <= 5`).
- **Third-Party Dependency & Dataset Rule:** Strictly permissive licences (`MIT`, `Apache-2.0`, `BSD`, `ISC`, `CC0-1.0`, `CC-BY-4.0`) logged in `THIRD_PARTY_LICENSES.md` and `ml/data/LICENSES.md`.

---

## 2. Ethics Approval / Institutional Exemption & DPDP Act 2023 Protocol

1. **Purpose Limitation & Data Minimisation:**
   - Photos collected for `LOOP-Images` depict inanimate pre-owned student goods (`electronics`, `furniture`, `books`, `hobbies`).
   - Photos collected for `LOOP-Scrub` use **exclusively staged mock documents** (synthetic printed campus ID cards, dummy license plates such as `MH 12 AB 0000`, dummy phone numbers `+91 90000 00000`, and consenting volunteer faces). Real Aadhaar, PAN, passport, or financial cards are strictly prohibited.
2. **Right to Withdraw & Erasure:**
   - Every volunteer image is indexed by an anonymous `volunteer_batch_id`. Upon withdrawal request, all associated images and derived embeddings are purged from Supabase Storage and dataset manifests within 24 hours.
3. **Blank Volunteer Photo & Staged Scrub Consent Form Template:**

```text
================================================================================
LOOP RESEARCH PROJECT — VOLUNTEER PHOTO & STAGED SCRUBBING CONSENT FORM (TEMPLATE)
Institution: Ajeenkya D Y Patil University, Pune
Investigators: Emmanuel George P, Sameer Makani
================================================================================
1. Purpose: I consent to provide photographs of pre-owned campus items (and/or
   staged background regions using mock IDs/plates) to train and evaluate the
   LOOP privacy-preserving reuse marketplace.
2. No Real Official IDs: I confirm that no real government ID, bank card, or
   non-consenting third party appears in my submitted photographs.
3. Storage & Anonymisation: My submission is stored under an anonymous batch ID
   separately from this consent record.
4. Right to Withdraw: I may request deletion of my contributed images at any
   time prior to final dataset freeze by quoting my anonymous receipt code.

Volunteer Anonymous Receipt Code: [LOOP-VOL-XXXX]
Consent Granted (Yes / No):       [   ]
Date:                             [YYYY-MM-DD]
================================================================================
(DO NOT COMMIT COMPLETED OR SIGNED FORMS TO GIT)
```

---

## 3. Multi-Annotator Ordinal Condition Labelling Guide (`ML_SPEC.md` §§1, 3)

Every listing in `LOOP-Images` is independently graded by **at least 2 annotators** on the 4-level ordinal scale (`0..3`). Disagreements are resolved by a 3rd tie-breaker annotator, and inter-annotator agreement is reported using **Quadratic Weighted Cohen's Kappa ($\kappa_w$)**.

| Ordinal Int | Grade Key | Visual Criteria Across Categories | Category-Specific Examples |
| :---: | :--- | :--- | :--- |
| **`3`** | `like_new` | Pristine cosmetic surface; zero scratches, dents, stains, or fraying; original packaging/accessories intact where applicable. | **Electronics:** Unscratched calculator screen, clean keys.<br>**Furniture:** Desk top with zero cup rings or edge chips.<br>**Books:** Uncreased spine, zero highlighting or pencil marks.<br>**Hobbies:** Guitar body with glossy finish, no pick wear. |
| **`2`** | `good` | Gently used with minor cosmetic wear visible only on close inspection; 100% structurally and functionally intact. | **Electronics:** Minor key shine on laptop/calculator, crisp display.<br>**Furniture:** Slight scuff on chair base, clean upholstery.<br>**Books:** Light corner shelf wear, clean readable pages (<5% pencil notes).<br>**Hobbies:** Badminton racket with slightly worn grip tape, intact strings. |
| **`1`** | `fair` | Noticeable surface scratches, scuffs, edge wear, or heavy highlighting across multiple regions, but remains usable. | **Electronics:** Scuffed outer casing or faded key legends.<br>**Furniture:** Visible scratches or stain on wooden tabletop.<br>**Books:** Creased cover, dog-eared pages, moderate highlighting.<br>**Hobbies:** Acoustic guitar with visible body dings or tarnished frets. |
| **`0`** | `poor` | Heavy structural or cosmetic damage, cracked housing, missing parts, torn pages, or requires repair before normal use. | **Electronics:** Cracked screen/bezel, missing battery cover.<br>**Furniture:** Broken chair armrest, deep gouges, wobbly leg.<br>**Books:** Torn cover, loose/missing pages, water damage.<br>**Hobbies:** Warped racket frame, broken tuning peg. |

> **Visual Inspection Ceiling Disclosure:** Annotators grade *visible surface condition only*. Functional or internal electronic defects (e.g., laptop battery health) cannot be inferred from photos and must be disclosed by the seller in the editable condition/description fields.

---

## 4. Staged `LOOP-Scrub` Annotation Protocol (`ML_SPEC.md` §6.2)

Annotators draw tight axis-aligned bounding boxes `(x, y, w, h)` normalized to `[0, 1]` over five sensitive PII classes:
1. `face`: Any visible human face (including background reflections or poster/photo frames).
2. `id_card`: Staged mock student/hostel ID cards or badges.
3. `plate`: Staged vehicle registration number plates.
4. `phone`: Printed or handwritten 10-digit Indian mobile numbers (`(\+91[\- ]?)?[6-9]\d{9}`).
5. `address`: Hostel room numbers, flat/street lines, or 6-digit Indian PIN codes (`\b\d{6}\b`).

**Primary Metric:** Per-class **Recall** is prioritized over precision (`ML_SPEC.md` §6.2) to minimize residual PII leak rate.
