# Phase 7 Acceptance & Verification Report

**Date:** 2026-11-21  
**Phase:** Phase 7 – On-Device Quality Check and Photo Privacy Scrubber  
**Status:** **PASSED**

---

## 1. Roadmap Acceptance Checks

| Criteria | Implementation & Evidence | Result |
| :--- | :--- | :---: |
| **Blurred image is what gets uploaded (original never reaches Storage)** | Verified in `apps/web/lib/scrubber.ts` & `InteractiveScrubberPreview.tsx`: `<canvas>` burns pixelation directly into export buffer before HTTP multipart transmission. | **PASS** |
| **Permissive-licence detection only (no YOLOv8)** | Detection models and regex adhere strictly to Apache 2.0 / MIT (BlazeFace/YuNet algorithms, regex OCR text filters). No AGPL-3.0 dependencies used. | **PASS** |
| **Quality checks (Laplacian variance & luminance)** | Implemented in `ml/src/quality_checker.py` and client-side `analyzeImageQuality` (detects blur, underexposure, and glare). | **PASS** |
| **OCR + regex for Indian contact numbers & addresses** | Validated in `ml/src/privacy_scrubber.py`: Indian mobile numbers (`(\+91[\- ]?)?[6-9]\d{9}`), PIN codes (`\b\d{6}\b`), and street tokens detected with precision. | **PASS** |
| **Server safeguard `/scrub-verify` blocks unblurred test face** | Validated in `apps/api/routers/scrub_verify.py` and tested in `test_scrubber_acceptance.py`. Rejects unblurred face signatures with HTTP 400 `UNSCRUBBED_SENSITIVE_DATA_DETECTED`. | **PASS** |
| **Interactive scrubber UI (add/resize/remove boxes)** | Delivered in `apps/web/components/InteractiveScrubberPreview.tsx` and wired into the `/sell` creation workflow. | **PASS** |
| **On-device vs Server experiment report produced** | Documented in `ml/reports/ondevice_vs_server/report.md` detailing latency (42ms mobile WASM vs 280ms server), accuracy parity ($< 1e-3$ deviation), and 68% upload payload savings. | **PASS** |

---

## 2. Deliverables Summary

- **ML & Detection (`ml/src`):**
  - `ml/src/quality_checker.py`: Variance of Laplacian and luminance heuristic analysis.
  - `ml/src/privacy_scrubber.py`: Permissive sensitive data detector for faces, plates, and phone/PIN patterns.
  - `ml/reports/ondevice_vs_server/report.md`: Comparative experiment report.
- **Backend & Safeguards (`apps/api`):**
  - `app/routers/scrub_verify.py`: `POST /api/v1/listings/{id}/scrub-verify` server-side fail-safe scanner.
  - `tests/test_scrubber_acceptance.py`: Acceptance test suite passing 4/4 checks.
- **Frontend (`apps/web`):**
  - `lib/scrubber.ts`: Irreversible canvas pixelation engine and fast client quality analyzer.
  - `components/InteractiveScrubberPreview.tsx`: Interactive preview allowing users to inspect detected regions, add custom boxes, delete false positives, and burn redaction.
  - `app/sell/page.tsx`: Embedded interactive scrubber into the photo upload stage of listing creation.
