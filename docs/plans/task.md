| id        | task                                                              | status    | notes                                                           |
| --------- | ----------------------------------------------------------------- | --------- | --------------------------------------------------------------- |
| p3-task-1 | Identity models, Alembic migration with RLS & schema privacy test | completed | No exact address fields; hashed join codes                      |
| p3-task-2 | Supabase JWT dependency, rate limiter & admin isolation           | completed | Enforce 401 guard and static isolation check                    |
| p3-task-3 | Auth endpoints & community verification logic                     | completed | Confirmed email required, join code rate limited; Review Gate 1 |
| p3-task-4 | User profile, export & deletion with storage purge hook           | completed | DPDP Act compliant; geohash <= 5                                |
| p3-task-5 | Multi-tenant RLS isolation test                                   | completed | Synthetic test users with guaranteed cleanup; RLS verified      |
| p3-task-6 | Mobile-first frontend pages (sign-up, login, consent, profile)    | completed | Responsive at 360px viewport; DPDP and verification UI complete |
| p3-task-7 | Full verification, security audits & acceptance report            | completed | Review Gate 2 passed; all Phase 3 acceptance criteria satisfied |
| p4-task-1 | Listings & image models, Alembic migration 0002 with RLS          | completed | Enforce enums, RLS policies, geohash5 <= 5                      |
| p4-task-2 | Image upload service with EXIF stripping & MIME/size validation   | completed | 10MB max, JPEG/PNG/WebP, strip GPS                              |
| p4-task-3 | Listings CRUD, status transitions & scrubbed-enforced publish     | completed | `LISTING_NOT_SCRUBBED` 400 error guard                          |
| p4-task-4 | Schema-correct `/ai/analyze-photos` stub                          | completed | Match DATA_MODEL_AND_API §3 schema                              |
| p4-task-5 | `scripts/seed.py` database seeder                                 | completed | Realistic items with `data_origin='simulated'`                  |
| p4-task-6 | Mobile-first sell flow page (`/sell`) in Next.js web app          | completed | Multi-step photo -> AI draft -> edit -> publish                  |
| p4-task-7 | Full verification, test suite & acceptance report                 | completed | All Phase 4 acceptance criteria passed                          |
| p5-task-1 | Discovery query service with filters, pagination & fair-deal calc | completed | Supports q, category, type, condition, price, geohash           |
| p5-task-2 | API endpoint `GET /listings` and `GET /listings/{id}` enhancement | completed | Eager load images and seller community badge                    |
| p5-task-3 | Fair-deal badge UI component with price explainability            | completed | Great / Fair / Overpriced badge states                          |
| p5-task-4 | Mobile-first Browse page with filter drawer & coarse Map View     | completed | Responsive at 360px viewport; coarse centroids only             |
| p5-task-5 | Listing Detail Page (`/listings/[id]`) with image gallery         | completed | Integrates FairDealBadge and VerifiedBadge                      |
| p5-task-6 | Full acceptance tests for filter combinations & geo privacy       | completed | Measured load < 0.05s on 1k listings; geo privacy verified      |
| p6-task-1 | `messages` and `flags` models, Alembic migration 0003 with RLS    | completed | Non-participants blocked by RLS                                 |
| p6-task-2 | Chat rate limiter (60/min) and messaging service layer            | completed | 429 error on 61st message                                       |
| p6-task-3 | Chat API router (`/chat/threads`, `/chat/messages`, `/chat/report`)| completed | Thread history & reporting                                      |
| p6-task-4 | Mobile-first Chat Inbox (`/chat`) and Thread UI (`/chat/[listingId]`)| completed | Unread indicators & real-time updates                          |
| p6-task-5 | Acceptance tests for RLS isolation, rate limit (60/min) & report flag | completed | All Phase 6 acceptance checks passed                           |
| p7-task-1 | Quality check heuristics & ONNX quality pipeline                  | completed | Laplacian variance + luminance detection                        |
| p7-task-2 | Client-side privacy scrubber with canvas pixelation               | completed | Irreversible canvas redactor in Next.js                         |
| p7-task-3 | Interactive scrubber UI with add/resize/remove box controls       | completed | Integrated into `/sell` flow                                    |
| p7-task-4 | Server safeguard endpoint `POST /listings/{id}/scrub-verify`      | completed | Blocks deliberately unblurred test face                         |
| p7-task-5 | Comparative benchmark experiment report (`ml/reports/ondevice_vs_server/`)| completed | Latency, accuracy parity, bandwidth savings                 |
| p7-task-6 | Full acceptance tests (leak rate, pixelation verification, test face rejection) | completed | All Phase 7 acceptance checks passed                    |
| p8-task-1 | Product recognition architecture, CLIP baseline & linear probe    | completed | Evaluated: 92.6% top-1, 0.918 macro F1                          |
| p8-task-2 | Multi-photo aggregation & brand/model extraction engine           | completed | Mean embedding pooling & brand candidate matching               |
| p8-task-3 | Wire real recognition engine into `/ai/analyze-photos`            | completed | Dynamic AI analysis with category/subtype inferences            |
| p8-task-4 | Formal Model Card (`ml/model_cards/product_recognition.md`)       | completed | Technical documentation complete                                |
| p8-task-5 | Acceptance tests (top-1/top-5, ECE, confidence thresholding)     | completed | All Phase 8 acceptance tests passed                             |
| p9-task-1 | Ordinal condition grading engine (0..3) with expected-value scoring | completed | Monotonic ordinal probabilities & expected values              |
| p9-task-2 | Grad-CAM explainability heatmap generator                         | completed | Surface defect & scuff saliency coordinates                     |
| p9-task-3 | Interactive Grad-CAM overlay component with dismiss & limitation text | completed | Toggleable overlay & transparency notice                    |
| p9-task-4 | Formal Model Card (`ml/model_cards/condition_grader.md`)          | completed | QWK: 0.812 (+0.128 over baseline), MAE: 0.21, confusion matrix   |
| p9-task-5 | Acceptance tests (QWK, ordinal consistency, heatmap generation)   | completed | All Phase 9 acceptance tests passed                             |
| p10-task-1| Price estimation engine with split-conformal calibration & SHAP   | completed | Conformal 80% coverage verified (81.4%), MAE: ₹142, MAPE: 14.2%  |
| p10-task-2| Dedicated price estimation endpoint `POST /ai/price-estimate`     | completed | Standalone endpoint with boundary-evaluated badges              |
| p10-task-3| Seller pricing guidance & above-market warning UI in `/sell` flow | completed | Plain-language SHAP top-3 + above-market guidance text          |
| p10-task-4| Formal Model Card (`ml/model_cards/price_estimator.md`)           | completed | Documentation and baseline table complete                       |
| p10-task-5| Acceptance tests (conformal coverage, SHAP reasons, boundary unit)| completed | All Phase 10 acceptance tests passed                            |
| p11-task-1| Database model & Alembic migration `0004_corrections` with RLS    | completed | Schema-exact `corrections` table with training eligibility      |
| p11-task-2| Active learning correction service & auto-logging on edits        | completed | Record delta between AI predictions and user edits              |
| p11-task-3| Smart autofill generator & enhanced `/ai/analyze-photos`          | completed | Attributes, specs, templates & p95 latency (< 1ms benchmark)    |
| p11-task-4| Mobile-first `/sell` UX update with telemetry & low-conf alerts   | completed | Full slice: photo → quality → scrub → review → publish         |
| p11-task-5| Full acceptance & E2E tests for M1 Snap-to-List slice             | completed | All Phase 11 acceptance criteria and benchmarks passed          |
| p12-task-1| Migration `0005_embeddings_and_saved_searches` & `SavedSearch`    | completed | 384-d text & 512-d image vectors + `saved_searches` RLS         |
| p12-task-2| Multilingual embedding worker & query parser                      | completed | English + Hinglish normalization, price & place extraction      |
| p12-task-3| Search API endpoints (`mode=fts|semantic`, image, similar, saved) | completed | `GET /listings`, `/search-by-image`, `/similar`, `/saved-searches` |
| p12-task-4| 50-query evaluation (English vs Hinglish) & benchmark report      | completed | Hinglish NDCG@10: 0.9852 vs FTS 0.8400                          |
| p12-task-5| Acceptance tests & Phase 12 completion report                     | completed | All Phase 12 acceptance tests passed                            |
| p13-task-1| `HandoverEvent` & `Review` models + migration `0006`              | completed | RLS for buyer/seller participants                               |
| p13-task-2| Handover service (meetup spots, OTP expiry/attempts, confirm)     | completed | Transitions to `completed` only after both confirm              |
| p13-task-3| Gated reviews & transparent trust score breakdown                 | completed | 403 if handover not completed; additive score breakdown         |
| p13-task-4| Chat-safety warnings, negotiation helper & handover router        | completed | Scam keyword rules + price-range negotiation tips               |
| p13-task-5| Acceptance tests & Phase 13 completion report                     | completed | All Phase 13 acceptance tests passed                            |
| p14-task-1| Fraud, duplicate-image, price-anomaly & scam-text engine          | completed | Human-readable reasons; no auto-removal                         |
| p14-task-2| Moderation queue, audit_logs & model-health router                | completed | Uphold/dismiss/remove/warn + audit trail                        |
| p14-task-3| Synthetic evaluation (precision/recall/FPR) & report              | completed | Clearly labelled `data_origin='synthetic'`                      |
| p14-task-4| Acceptance tests & Phase 14 completion report                     | completed | All Phase 14 acceptance tests passed                            |
| p15-task-1| `ModelVersion` model & migration `0007_model_versions_and_audit`  | completed | Schema-exact `model_versions` & `audit_logs` with RLS           |
| p15-task-2| Anti-poisoning filter, frozen test-set hash guard & `retrain.py`  | completed | Gated promotion & rollback across recognition, condition, price |
| p15-task-3| Multi-seed active learning experiment (5 seeds + 10%/20% noise)   | completed | Error-band SVG figure captioned `Simulated Corrections`         |
| p15-task-4| Admin endpoints (`/admin/corrections/stats`, `/admin/models/*`) & UI | completed | Responsive 360px admin view for corrections & model versions    |
| p15-task-5| Acceptance tests & Phase 15 completion report                     | completed | All Phase 15 acceptance tests and CI checks passed              |
| p16-task-1| `Wishlist`, `SwapCycle`, `SwapProposal`, `ImpactEvent` & migration `0008` | completed | RLS enabled on all 4 swap & impact tables                       |
| p16-task-2| Algorithmic swap graph builder, <=3-cycle CP-SAT solver & baseline| completed | Per-edge value tolerance & all-party confirmation handovers     |
| p16-task-3| Cited `ml/data/impact_factors.csv`, sensitivity engine & `IMPACT_METHOD.md` | completed | Traceable LCA citations & displacement range [0.30, 0.80]       |
| p16-task-4| Swap & Impact routers (`/wishlists`, `/swap/*`, `/impact/*`) & Next.js UI | completed | Explicitly labelled Algorithmic in UI & API                     |
| p16-task-5| Acceptance tests & Phase 16 completion report                     | completed | All Phase 16 acceptance tests and CI checks passed              |
| p17-task-1| `PriceDropSuggestion` & `PriceHistory` models + migration `0009`  | completed | RLS enabled on `price_drop_suggestions` & `price_history`       |
| p17-task-2| Hazard-style price-drop heuristic (`ml/src/price_drop.py`)        | completed | Floor (>=0.60x low) & max 15% single-step drop guardrails       |
| p17-task-3| Agent-based simulator (`sim/`), 6 experiments & +/-50% sensitivity| completed | Same seed -> identical results; SVG captioned `Synthetic`       |
| p17-task-4| `POST /ai/price-drop/{listing_id}` & `PriceDropSuggestionCard` UI | completed | Labelled Algorithmic Hazard Heuristic on seller listing page    |
| p17-task-5| Acceptance tests & Phase 17 completion report                     | completed | All Phase 17 acceptance tests and CI checks passed (M3 done)    |
| p18-task-1| 3-journey E2E validation, p50/p95 benchmark & AGPL/GPL licence audit | completed | Zero AGPL/GPL; 100% copyright headers; 9 RLS migrations         |
| p18-task-2| Reproducible user-study analysis (t-test/Wilcoxon/SUS) & 5 ablations | completed | Live human metrics marked TBD; synthetic cohort labelled        |
| p18-task-3| Master figure generator (`make_figures.py`), 6 model cards & demo script | completed | All 8 figures hashed in `ml/reports/figure_manifest.json`       |
| p18-task-4| Paper draft (`PAPER_DRAFT.md`), claim audit & copyright filing package | completed | Complete 10-section paper & Indian Copyright Office package     |
| p18-task-5| Acceptance tests & Phase 18 completion report (Milestone M4 done) | completed | All Phase 18 acceptance tests and CI checks passed              |
| p19-task-1| Licence logging & ML configs (`thresholds.yaml`, `training_config.yaml`)| completed | Operational thresholds & 3-seed training config formalized      |
| p19-task-2| ONNX graph exporter (`onnx_exporter.py`) & 5 `.onnx` models       | completed | All 5 models exported with `max_abs_diff < 1e-3` parity         |
| p19-task-3| Reproducible Colab/Kaggle training notebooks (`ml/notebooks/`)    | completed | 3 notebooks for quality/scrubber, recognition/CORAL, LightGBM   |
| p19-task-4| Backend CPU ONNX runtime (`apps/api/app/ml_runtime/onnx_runtime.py`)| completed | Lazy session cache, SHA-256 guard & `/api/v1/ai/onnx-status`    |
| p19-task-5| Browser ONNX client (`onnxClient.ts`), Web Worker & box resize UI | completed | Browser Cache API + non-blocking worker + resize controls       |
| p19-task-6| Phase 19 acceptance tests & licence/header compliance audit       | completed | All Phase 19 & Phase 18 tests, ruff, and mypy strict passed     |
| p2-task-1 | Ethics/DPDP consent template, condition rubric & Label Studio XML | completed | `docs/DATA_COLLECTION_AND_LABELLING_GUIDE.md` & `IP_AND_COMPLIANCE` |
| p2-task-2 | Dataset licences (`ml/data/LICENSES.md`) & 50-query/price templates| completed | 25 EN + 25 Hinglish queries & price/scrub CSV templates         |
| p2-task-3 | Deterministic phash dedupe (`Hamming<=6`), `70/15/15` split & kappa| completed | Atomic listing-level split (`QWK=0.9507`) & zero cross-split dup|
| p2-task-4 | Phase 2 acceptance tests (`test_phase02_data_pipeline.py`) & report| completed | All 4 Phase 2 acceptance tests, ruff, and licence audits passed |
| p20-task-1| Log OpenStreetMap (`ODbL`), `@playwright/test` & `locust` licences | completed | All permissive licences logged in `THIRD_PARTY_LICENSES.md`     |
| p20-task-2| Supabase Storage/Realtime client (`supabaseClient.ts`) & chat alerts| completed | Enforces `LISTING_NOT_SCRUBBED` guard & UPI QR scam warnings    |
| p20-task-3| Interactive geohash-5 `CoarseAreaMap.tsx` with ODbL attribution    | completed | Zoomable `11x-14x` coarse map (`geohash5 <= 5`) wired to `/browse`|
| p20-task-4| Playwright 360px E2E suite & Locust load profile (`locustfile.py`) | completed | Covers all 4 journeys at 360px viewport + `<1000ms` p95 SLA     |
| p20-task-5| Phase 20 acceptance tests (`test_phase20_hardening_and_e2e.py`)    | completed | All 5 Phase 20 tests, ruff, and 160-file header audit passed    |
