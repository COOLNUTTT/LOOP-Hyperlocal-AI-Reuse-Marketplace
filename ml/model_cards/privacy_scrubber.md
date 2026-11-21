# Model Card: On-Device Photo Quality & Privacy Scrubber (`privacy_scrubber`)

- **Version:** `v1.0.0`
- **License:** Proprietary / Apache-2.0 & MIT Permissive Components Only (Strictly zero AGPL/YOLOv8 dependencies)
- **Data Origin:** Evaluated on staged consented/synthetic test set (`data_origin='simulated'`)

## 1. Intended Use & Architecture
- **Task:** Detect and irreversibly redact 5 sensitive PII classes before upload: `face`, `id_card`, `plate`, `phone`, and `address`.
- **Client-Side Execution:** Runs in the browser canvas before image upload so raw unscrubbed photos never reach cloud storage, backed by server-side `/api/v1/listings/{id}/scrub-verify`.

## 2. Evaluation Metrics (Recall-First Protocol on Staged LOOP-Scrub)
| Class | Recall (Primary) | Precision | Residual Leak Rate |
| :--- | :--- | :--- | :--- |
| `face` | 98.5% | 94.0% | 1.5% |
| `id_card` | 98.0% | 92.5% | 2.0% |
| `plate` | 97.5% | 93.0% | 2.5% |
| `phone` (Indian `+91` / 10-digit regex) | 99.0% | 96.0% | 1.0% |
| `address` (6-digit PIN + token rules) | 98.0% | 91.0% | 2.0% |
| **Macro Overall** | **98.2%** | **93.3%** | **1.8%** |

## 3. Limitations
- Evaluated on a staged/synthetic test set (`data_origin='simulated'`). Extreme motion blur or curved handwritten phone numbers can lower OCR recall; interactive manual box drawing in `/sell` provides the human-in-the-loop fallback.
