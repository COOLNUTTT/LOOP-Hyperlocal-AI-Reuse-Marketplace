# Phase 22: Full-Stack Bugfix & Hardening Plan

> **Goal:** Resolve all 9 bugs identified during the full-project audit across backend auth/DB dependencies, frontend API routing & `/sell` publish flow, TypeScript Web Worker compilation, health/swap route alignment, DPDP storage purge prefixing, and linter/typechecker hygiene.

---

## 1. Bug Fixes & Architecture

1. **Bug 1 — `get_current_db_user` Dependency (`apps/api/app/dependencies/auth.py` & 7 Routers):**
   - `get_current_user` returns `AuthenticatedUser` (`auth_uid`, `email`, `is_confirmed`, `raw_payload`), which lacks `.id` and `.role`.
   - Add `get_current_db_user(auth_user: AuthenticatedUser = Depends(get_current_user), db: Optional[AsyncSession] = Depends(get_db)) -> User` that queries `User` by `User.auth_uid == auth_user.auth_uid` (or auto-provisions/raises `401` if missing) and preserves compatibility with existing test dependency overrides of `get_current_user` (if a test overrides `get_current_user` to return a `User` ORM instance, handle both `User` and `AuthenticatedUser` cleanly!).
   - Wire `listings.py`, `chat.py`, `handover.py`, `moderation.py`, `saved_searches.py`, `swap.py`, and `impact.py` to use `get_current_db_user` (and `scrub_verify.py` if applicable).

2. **Bug 2 — Frontend API Proxy & Consistent `NEXT_PUBLIC_API_URL` (`apps/web/next.config.mjs`, `apps/web/lib/supabaseClient.ts`):**
   - Add `async rewrites()` in `apps/web/next.config.mjs` proxying `/api/v1/:path*` to `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/:path*` so all relative `fetch("/api/v1/...")` calls in `login`, `register`, `profile`, and `sell` work seamlessly in local dev, Docker Compose, and Vercel + Render.
   - Standardize `getSupabaseConfig().apiUrl` in `apps/web/lib/supabaseClient.ts` so `NEXT_PUBLIC_API_URL` is consistently treated as the base origin (`http://localhost:8000`), appending `/api/v1` only once.

3. **Bug 3 — Complete `/sell` Publish Flow (`apps/web/app/sell/page.tsx`):**
   - After `POST /api/v1/listings` creates the draft listing (`listingData.id`), convert the scrubbed canvas data URL to a `Blob`, upload it via `POST /api/v1/listings/${listingData.id}/images` with `scrubbed=true`, and call `POST /api/v1/listings/${listingData.id}/publish` so the listing transitions from `draft` to `active`.

4. **Bug 4 — Inject `db` Session in `auth.py` & `users.py` Routers (`apps/api/app/routers/auth.py`, `users.py`):**
   - Inject `db: Annotated[Optional[AsyncSession], Depends(get_db)] = None` in `auth.py` (`/register`, `/verify-community`) and `users.py` (`/me`, `/me/export`, `/me` DELETE) and pass `db=db` to `auth_service` and `user_service` so database writes persist whenever Postgres is configured.

5. **Bug 5 — Fix TypeScript Web Worker Compilation (`apps/web/lib/scrubber.worker.ts`):**
   - Type the worker global scope via `const workerScope = self as unknown as { onmessage: ((ev: MessageEvent<ScrubberWorkerRequest>) => void) | null; postMessage: (msg: ScrubberWorkerResponse) => void };` so `tsc --noEmit` and `next build` pass cleanly under `"lib": ["dom", "dom.iterable", "esnext"]` without requiring `"webworker"` lib conflicts.

6. **Bug 6 — Align `/api/v1/health` & `/api/v1/swap/cycles` (`apps/api/app/main.py`, `infra/load/locustfile.py`):**
   - Mount `health.router` at both root (`/health`, required by `ci.yml` and `docker-compose`) and `/api/v1` (`/api/v1/health`, required by `render.yaml` and `locustfile.py`).
   - Update `infra/load/locustfile.py` to call `GET /api/v1/swap/proposals` (or add `GET /api/v1/swap/cycles` / align with existing `swap.py` route).

7. **Bug 7 — DPDP Storage Purge Prefix Alignment (`apps/api/app/services/admin_service.py` & `apps/api/app/services/user_service.py`):**
   - Support purging both `{auth_uid}/` and `listings/{listing_id}/` prefixes when a user deletes their account via `DELETE /api/v1/users/me` (`purge_user_storage(auth_uid, listing_ids=...)`).

8. **Bug 8 — Fix All 7 `ruff` Unused-Import Errors (`ml/`, `scripts/seed.py`):**
   - Clean unused imports in `ml/notebooks/01_quality_and_scrubber_onnx.ipynb`, `ml/src/eval_semantic_search.py`, `ml/src/semantic_search.py`, `ml/src/smart_autofill.py`, and `scripts/seed.py`.

9. **Bug 9 — Fix Root `mypy` PIL Import Check (`apps/api/app/services/image_service.py`):**
   - Add `# type: ignore[import-not-found, import-untyped]` or `ignore_missing_imports` handling on `from PIL import Image` so `mypy` passes both from `apps/api/` and from the repository root.

---

## 2. Task Breakdown

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p22-task-1 | Add `get_current_db_user` in `auth.py`, wire 7 routers, and pass `db` in `auth.py`/`users.py` | completed | Resolves `AuthenticatedUser` to Postgres `User` + greenlet guard |
| p22-task-2 | Add `/api/v1` rewrite in `next.config.mjs`, fix `supabaseClient.ts` `apiUrl`, complete `/sell` image+publish flow, and fix `scrubber.worker.ts` TS types | completed | Fixes frontend routing, publish lifecycle & `tsc` error |
| p22-task-3 | Mount `/api/v1/health`, fix `locustfile.py` swap route, fix `purge_user_storage` listing prefixes, and clean 7 `ruff` + `mypy` `PIL` issues | completed | Fixes 404s, DPDP purge, `ruff` & `mypy` |
| p22-task-4 | Write `apps/api/tests/test_phase22_bugfixes.py` regression tests, verify full `pytest`/`ruff`/`mypy`/`black`/audit, and commit | completed | All 116 tests + ruff + black + mypy + audits passed |
