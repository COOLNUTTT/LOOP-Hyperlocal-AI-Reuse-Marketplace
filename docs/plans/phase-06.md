# Phase 6: Realtime Chat and Notifications Implementation Plan

> **Goal:** Implement the complete chat and messaging lifecycle: database schema for `messages` with RLS, Alembic migration 0003, real-time message sending and retrieval with rate limiting (60 messages/minute ceiling), report/block functionality that writes `manual_report` flags, in-app notifications, and a responsive mobile-first chat UI (`/chat` and `/chat/[listingId]`).

---

### Approved Architecture & Constraints

1. **Database Schema & RLS (`messages` table):**
   - Columns:
     - `id` (UUID PK), `listing_id` (FK `listings.id`), `sender_id` (FK `users.id`), `receiver_id` (FK `users.id`).
     - `body` (Text, 1..2000 chars), `flagged_scam` (Boolean default `false`), `read_at` (DateTime nullable), `created_at` (DateTime with timezone).
   - RLS Policy:
     - Non-participants cannot view messages. `SELECT` allowed ONLY if `auth.uid()` belongs to `sender_id` OR `receiver_id`.
     - `INSERT` allowed ONLY if `auth.uid()` matches `sender_id` and the user is participant in the listing thread.

2. **Flags & Moderation (`flags` table):**
   - Block/report functionality creates a `manual_report` flag in `flags` table with target `listing_id` or `message_id`.

3. **Rate Limiting:**
   - Enforce a strict ceiling of **60 messages per minute** per user on sending messages. Returns HTTP 429 Too Many Requests if exceeded.

4. **API Endpoints (`/api/v1/chat`):**
   - `GET /chat/threads`: List conversations/threads for current user with latest message, unread status, and other party info.
   - `GET /chat/threads/{listing_id}`: Get message history for a specific listing thread between current user and other party.
   - `POST /chat/messages`: Send a message in a thread. Enforces 60/min rate limit.
   - `POST /chat/messages/{id}/read`: Mark message as read.
   - `POST /chat/report`: Report a user/message (creates `manual_report` flag).

5. **Frontend UI (`apps/web`):**
   - `/chat`: Thread inbox showing active conversations, listing thumbnail, counterparty name, and unread badges.
   - `/chat/[listingId]`: Realtime chat thread with message bubbles, timestamp, negotiation shortcuts (e.g., "Is this available?", "Offer ₹X"), and report user button.
   - Chat entrypoint on `/listings/[id]` page ("Chat with Seller" button wired directly).

---

### Tasks

| id | task | status | notes |
| :--- | :--- | :--- | :--- |
| p6-task-1 | `messages` and `flags` models, Alembic migration 0003 with RLS | in_progress | Non-participants blocked by RLS |
| p6-task-2 | Chat rate limiter (60/min) and messaging service layer | not_started | 429 error on 61st message |
| p6-task-3 | Chat API router (`/chat/threads`, `/chat/messages`, `/chat/report`) | not_started | Thread history & reporting |
| p6-task-4 | Mobile-first Chat Inbox (`/chat`) and Thread UI (`/chat/[listingId]`) | not_started | Unread indicators & real-time updates |
| p6-task-5 | Acceptance tests for RLS isolation, rate limit (60/min) & report flag | not_started | Phase 6 acceptance checks |
