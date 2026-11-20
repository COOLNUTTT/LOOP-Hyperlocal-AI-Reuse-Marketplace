# Phase 7: On-Device Quality Check and Photo Privacy Scrubber Implementation Plan

> **Goal:** Implement the dual on-device inference pipeline and server safeguards:
> 1. Photo quality assessment (blur detection via variance of Laplacian, darkness check via mean luminance, and MobileNetV3-Small ONNX architecture).
> 2. Privacy Scrubber: permissive-licence face detection (BlazeFace/YuNet), vehicle number plate/ID card detection, and OCR + regex for Indian mobile numbers (`(\+91[\- ]?)?[6-9]\d{9}`) and addresses (PIN codes `\b\d{6}\b`, tokens like "Flat", "Nagar").
> 3. Client-side irreversible pixelation/blurring on `<canvas>` ensuring unscrubbed raw pixels NEVER leave the device.
> 4. Interactive scrubber preview UI: users can add, resize, and remove detected sensitive bounding boxes.
> 5. Server safeguard endpoint `POST /api/v1/listings/{id}/scrub-verify`: verifies that uploaded photos contain no unscrubbed sensitive faces or plates, blocking publication with HTTP 400 if unscrubbed items remain.
> 6. On-device vs server experiment report (`ml/reports/ondevice_vs_server/report.md`): accuracy parity, latency p50/p95, payload savings, compute avoided.

---

### Approved Architecture & Constraints

1. **Permissive Licensing Guarantee:**
   - Detectors strictly use Apache 2.0 / MIT / BSD models (e.g. BlazeFace, YuNet, YOLOX-Nano).
   - **Ultralytics YOLOv8 (AGPL-3.0) is strictly prohibited.**

2. **Quality Heuristics & Metrics:**
   - Blur detection: Variance of Laplacian threshold ($T_{\text{blur}} = 100$).
   - Darkness detection: Mean luminance threshold ($T_{\text{dark}} = 40$).
   - Overexposure threshold: Mean luminance threshold ($T_{\text{bright}} = 220$).

3. **Client-Side Privacy Scrubber (`apps/web/lib/scrubber.ts` & UI component):**
   - Detects:
     - Faces (BlazeFace / lightweight Haar/cascade emulator).
     - Number plates & ID cards (geometric aspect ratio & texture detector).
     - Sensitive text (Indian phone numbers: `(\+91[\- ]?)?[6-9]\d{9}`, PIN codes: `\b\d{6}\b`).
   - Canvas pixelation: Irreversible downscale-upscale pixelation or heavy Gaussian blur on detected bounding boxes.
   - User interaction: Interactive bounding box controls (add box, delete box, adjust size).

4. **Server Safeguard Endpoint (`POST /api/v1/listings/{id}/scrub-verify`):**
   - Server-side inspection verifying that no unblurred human face or legible plate is exposed in the final uploaded asset.
   - If an unblurred sensitive face/ID is detected, returns HTTP 400 with `UNSCRUBBED_SENSITIVE_DATA_DETECTED` and prompts the user to apply redaction.

5. **Experimental Benchmark Report (`ml/reports/ondevice_vs_server/report.md`):**
   - Documented comparative latency, throughput, model footprint, and byte savings between client-side WebAssembly inference vs server roundtrips.

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p7-task-1 | Quality check heuristics (Laplacian variance, luminance) & ONNX quality pipeline | in_progress | Python service + browser JS utility |
| p7-task-2 | Client-side privacy scrubber (faces, plates, phone/PIN regex) with canvas pixelation | not_started | Irreversible canvas redactor in Next.js |
| p7-task-3 | Interactive scrubber UI with add/resize/remove box controls | not_started | Integrated into `/sell` flow |
| p7-task-4 | Server safeguard endpoint `POST /listings/{id}/scrub-verify` | not_started | Blocks deliberately unblurred test face |
| p7-task-5 | Comparative benchmark experiment report (`ml/reports/ondevice_vs_server/`) | not_started | Accuracy parity, latency, bandwidth savings |
| p7-task-6 | Full acceptance tests (leak rate, pixelation verification, test face rejection) | not_started | Phase 7 acceptance checks |
