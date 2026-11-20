# Benchmark Experiment: On-Device Quality Assessment vs Server Inference

**Date:** 2026-11-21  
**Author:** Emmanuel George P & Sameer Makani  
**Experiment Target:** MobileNetV3-Small & Laplacian Quality Model (Roadmap Phase 7 / ML_SPEC §6.1)

---

## 1. Executive Summary

To guarantee user privacy under the Digital Personal Data Protection (DPDP) Act, 2023, LOOP enforces on-device photo quality and privacy scrubbing. Raw unblurred photos containing identifiable human faces, license plates, or contact numbers must never traverse the network.

This benchmark compares the performance, accuracy parity, and bandwidth impact of **Client-Side WebAssembly/Canvas (`onnxruntime-web`)** execution versus standard **Server CPU API processing**.

---

## 2. Experimental Setup

- **Model:** MobileNetV3-Small quality classifier + discrete Laplacian edge variance.
- **Client Devices Tested:**
  1. Mid-range Mobile Device (Snapdragon 778G, Chrome Mobile PWA).
  2. Laptop / Desktop Client (Core i7 / Apple M-series, Chrome Desktop).
- **Server Environment:** 2 vCPU Linux Container, Python 3.11, ONNX Runtime 1.17 (CPU Execution Provider).
- **Test Set:** 250 evaluation photos (sharp, motion-blurred, under-exposed, over-exposed, and containing sensitive personal data).

---

## 3. Comparative Results

| Evaluation Metric | Client-Side (WASM / Browser) | Server-Side (REST API) | Delta / Benefit |
| :--- | :---: | :---: | :---: |
| **Sharpness / Blur Parity** | 99.8% match | 100.0% (baseline) | Parity within 1e-3 ($< 0.2\%$ deviation) |
| **Luminance Parity** | 100.0% match | 100.0% (baseline) | Exact integer match on 256×256 canvas |
| **Mobile Latency (p50)** | **42 ms** | 280 ms (incl. RTT) | **6.6× faster user feedback** |
| **Mobile Latency (p95)** | **88 ms** | 640 ms (incl. network variance) | **7.2× faster under variable 4G** |
| **Laptop Latency (p50)** | **14 ms** | 165 ms | **11.7× faster** |
| **Unscrubbed Image Bytes Leaked** | **0 Bytes** (100% prevented) | 4.2 MB average per photo | **Zero raw privacy leakage** |
| **Bandwidth Upload Saved** | **68% reduction** | 0% (Full raw payload sent) | Downscaled pixelated JPEG |
| **Server Compute Incurred** | **0 ms CPU** | ~85 ms CPU per upload | **100% server compute avoided** |

---

## 4. Key Takeaways & Compliance Guarantee

1. **Deterministic Privacy Guarantee:**
   Because pixelation and blurring are executed in-memory on the client `<canvas>` prior to network dispatch, raw photos never leave the browser sandbox.
2. **Server Safeguard Endpoint:**
   The secondary `/api/v1/listings/{id}/scrub-verify` endpoint acts as a fail-safe firewall, blocking any deliberately bypassed or unscrubbed human faces with HTTP 400.
3. **Bandwidth & Compute Efficiency:**
   Offloading quality and redaction checks eliminates over 68% of uploaded network bytes and frees server threads for transactional operations.
