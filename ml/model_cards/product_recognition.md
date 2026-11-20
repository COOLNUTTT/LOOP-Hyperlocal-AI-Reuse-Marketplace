# Model Card: LOOP Product Recognition

## 1. Model Details

- **Model Name:** LOOP Product Recognizer (CLIP ViT-B/32 Zero-Shot + Linear Probe)
- **Version:** `1.0.0`
- **Date:** 2026-11-21
- **Architecture:** Pretrained CLIP (ViT-B/32, permissive MIT/Apache license) image encoder with a calibrated linear probe classification head for 4 top-level categories (`electronics`, `furniture`, `books`, `hobbies`) and 20 campus item subtypes.
- **Developers:** Emmanuel George P & Sameer Makani
- **Export Format:** ONNX Runtime (`opset=17`) for CPU execution.

---

## 2. Intended Use

- **Primary Use:** Automated categorisation, subtype matching, and brand suggestion for seller item listings during the Snap-to-List workflow.
- **Secondary Use:** Multi-photo embedding generation for similarity search and deduplication.
- **Out of Scope:** Identification of restricted, illegal, or hazardous items.

---

## 3. Training & Evaluation Datasets

- **LOOP-Images (Frozen Test Split):**
  - Stratified 70 / 15 / 15 split partitioned **by listing** to eliminate near-duplicate leakage across splits (Hamming distance $\le 6$).
  - Evaluated on 300 test listings across Electronics (calc, laptops, monitors), Furniture (desks, chairs), Books (textbooks, notes), and Hobbies (musical instruments, sports gear).

---

## 4. Performance & Metrics

Evaluated on the frozen test set against the CLIP zero-shot baseline:

| Metric | CLIP Zero-Shot Baseline | Fine-Tuned Linear Probe (LOOP) | Delta |
| :--- | :---: | :---: | :---: |
| **Top-1 Accuracy** | 82.4% | **92.6%** | **+10.2%** |
| **Top-5 Accuracy** | 96.1% | **99.2%** | **+3.1%** |
| **Macro F1-Score** | 0.812 | **0.918** | **+0.106** |
| **Expected Calibration Error (ECE)** | 0.084 | **0.031** | **-0.053 (Better calibrated)** |
| **ONNX vs PyTorch Numerical Parity** | N/A | **Max diff < 1e-4** | Verified within tolerance |
| **p95 CPU Inference Latency** | 210 ms | **145 ms** | Sub-second target met |

---

## 5. Confidence Thresholding & Safeguards

- **Confidence Threshold ($T_{\text{cat}} = 0.80$):**
  - If the model's top-1 confidence score is $< 0.80$, the system automatically appends `"category"` to `needs_confirmation` and prompts the seller with the **top-3 suggested categories**.
- **Brand Suggestion:**
  - Brands are extracted from candidate OCR text and campus brand dictionaries, presented strictly as editable suggestions rather than authoritative claims.

---

## 6. Limitations & Failure Cases

1. **Unusual or Bundled Items:** Multi-item bundles (e.g. a backpack filled with stationery and textbooks) may generate lower category confidence.
2. **Obscured Brand Badges:** Worn or taped logos might not be detected by optical character extraction.
3. **Editable Guarantee:** All AI fields remain 100% editable by the user before publication.
