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
| p8-task-3 | Wire real recognition engine into `/ai/analyze-photos`     | completed | Dynamic AI analysis with category/subtype inferences            |
| p8-task-4 | Formal Model Card (`ml/model_cards/product_recognition.md`)       | completed | Technical documentation complete                                |
| p8-task-5 | Acceptance tests (top-1/top-5, ECE, confidence thresholding)     | completed | All Phase 8 acceptance tests passed                             |
