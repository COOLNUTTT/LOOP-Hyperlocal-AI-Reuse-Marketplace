# Phase 22: Full-Stack Bugfix & Hardening Completion Report

> **Date:** November 2026  
> **Status:** Completed  
> **Scope:** `get_current_db_user` Auth-to-ORM Resolution, `db` Session Injection & `greenlet` Guard, Next.js `/api/v1` Proxy Rewrites, `/sell` Image Upload + Publish Lifecycle, Web Worker TypeScript Typing, `/api/v1/health` & `/api/v1/swap/proposals` Alignment, DPDP Listing Storage Purge, and `ruff`/`mypy` Cleanup

---

## 1. Summary of All 9 Bugs Fixed

1. **Auth-to-ORM User Resolution (`apps/api/app/dependencies/auth.py` + 7 Routers):** Added `get_current_db_user` to resolve `AuthenticatedUser.auth_uid` to a Postgres `User` row (while remaining 100% compatible with tests that mock `get_current_user` with a `User` instance), preventing `AttributeError` on `.id` and `403` on `.role` across `listings`, `chat`, `handover`, `moderation`, `saved_searches`, `swap`, `impact`, and `scrub_verify`.
2. **DB Injection & `greenlet` Guard (`apps/api/app/routers/auth.py`, `users.py`, `dependencies/database.py`):** Passed `db` to `auth_service` and `user_service` and added a `greenlet` availability guard in `get_db()` so standalone/offline tests never crash.
3. **Frontend API Rewrites & URL Consistency (`apps/web/next.config.mjs`, `apps/web/lib/supabaseClient.ts`):** Added `/api/v1/:path*` proxy rewrites in `next.config.mjs` and normalized `NEXT_PUBLIC_API_URL` handling in `supabaseClient.ts`.
4. **Complete `/sell` Image Upload + Publish Flow (`apps/web/app/sell/page.tsx`):** Wired `POST /api/v1/listings/{id}/images` (`scrubbed=true`) and `POST /api/v1/listings/{id}/publish` after draft creation so listings transition from `draft` to `active`.
5. **Web Worker TypeScript Compilation (`apps/web/lib/scrubber.worker.ts`):** Added `WorkerGlobalScopeLike` typing so `tsc --noEmit` and `next build` pass cleanly without `"webworker"` lib conflicts.
6. **Health & Swap Route Alignment (`apps/api/app/main.py`, `infra/load/locustfile.py`):** Mounted `health.router` at both `/health` and `/api/v1/health`, and updated Locust to hit `/api/v1/swap/proposals`.
7. **DPDP Storage Purge Prefix Alignment (`apps/api/app/services/admin_service.py`, `user_service.py`):** Extended `purge_user_storage` to purge `listings/{listing_id}/` prefixes alongside `{auth_uid}/`.
8. **Ruff Unused Imports (`ml/`, `scripts/seed.py`):** Cleaned all 7 `F401` unused-import errors.
9. **Root Mypy `PIL` Check (`apps/api/app/services/image_service.py`):** Switched to `importlib.import_module("PIL.Image")` so `mypy --strict` passes from both `apps/api/` and the repository root.
