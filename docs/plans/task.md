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
