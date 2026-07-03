# Plan

This plan breaks the project into 10 parts. Each part has:
- **Substeps** — a checklist the agent works through in order.
- **Tests** — what must be verified.
- **Success criteria** — the bar for "done."

A part is complete only when every substep is checked, every test passes, and every success criterion is met. Pause for user review after Part 1, Part 5, and Part 8 (the plan-and-approve gates).

Cross-cutting rules:
- Follow [AGENTS.md](../AGENTS.md) for coding standards, colors, and library choices.
- Update each area's `AGENTS.md` as that area takes shape.
- Prefer the latest idiomatic library versions per AGENTS.md.
- No defensive code for scenarios that can't happen. Keep it simple.
- One commit per part once tests and success criteria are green.

---

## Part 1: Plan

- [x] Read AGENTS.md, docs/PLAN.md, and the existing frontend.
- [x] Create [frontend/AGENTS.md](../frontend/AGENTS.md) describing the existing code.
- [x] Enrich docs/PLAN.md with detailed substeps, tests, and success criteria for all 10 parts.
- [ ] Get user sign-off on the plan.

**Tests:** N/A — planning phase.

**Success criteria:**
- `frontend/AGENTS.md` exists and accurately describes the existing frontend (stack, layout, state model, components, tests, known discrepancies).
- `docs/PLAN.md` contains detailed substeps, tests, and success criteria for all 10 parts.
- User has reviewed and approved the plan.

---

## Part 2: Scaffolding

- [x] Decide and document in `backend/AGENTS.md`:
  - Python version (3.13).
  - FastAPI + Uvicorn (latest).
  - Host port 8000, container name `pm-app`.
- [x] Create `backend/pyproject.toml` for uv with runtime deps (`fastapi`, `uvicorn[standard]`) and dev deps (`pytest`, `httpx2`).
- [x] Create `backend/app/__init__.py` and `backend/app/main.py` with `GET /` and `GET /api/health`.
- [x] Create `backend/tests/__init__.py` and `backend/tests/test_health.py` using `TestClient`.
- [x] Create `Dockerfile` (single-stage Python 3.13 + uv) at repo root, build context = repo root.
- [x] Create `.dockerignore` at repo root.
- [x] Create `scripts/start.sh`, `scripts/stop.sh`, `scripts/start.bat`, `scripts/stop.bat`; mark shell scripts executable.
- [x] Update `backend/AGENTS.md` and `scripts/AGENTS.md` with descriptions.

**Tests:**
- Unit: `cd backend && uv run pytest` — both tests pass.
- Manual: `bash scripts/start.sh` builds + runs; `curl /` returns the hello-world HTML; `curl /api/health` returns `{"status": "ok"}`; `bash scripts/stop.sh` stops and removes the container.

**Success criteria:**
- `docker build` succeeds.
- `docker run` starts the container.
- `GET /` returns 200 with hello-world HTML.
- `GET /api/health` returns 200 with `{"status": "ok"}`.
- `pytest` passes.
- Start and stop scripts work on Mac/Linux.

---

## Part 3: Add in Frontend

- [x] Resolve color scheme discrepancy: migrated to spec colors (Accent Green / Primary Indigo / Secondary Cyan / Dark Slate / Gray Text). CSS variables and inline rgba values updated across `globals.css` and all components.
- [x] Configure static export in `frontend/next.config.ts` (`output: 'export'`, `images.unoptimized: true`, `trailingSlash: true`).
- [x] Verify `npm run build` produces a clean `frontend/out/` directory.
- [x] Decide on font strategy: keep `next/font/google` (Google Fonts downloaded at build time). Documented in `frontend/AGENTS.md`; Docker builder needs network access.
- [x] Update `Dockerfile` to a multi-stage build: `node:22-slim` builder runs `npm ci` + `npm run build`; final `python:3.13-slim` image copies `out/` to `/app/static`.
- [x] Update `backend/app/main.py` to serve the static frontend via `StaticFiles(directory="/app/static", html=True)` mounted at `/`. Exposed a `create_app(static_dir=None)` factory so tests can inject a temp directory.
- [x] Backend tests: added `tests/test_frontend.py` covering `GET /` (returns static index with "Kanban Studio") and `GET /_next/static/<file>` (returns asset content).

**Tests:**
- Unit (frontend): `cd frontend && npm run test:unit` — 6 tests pass (`moveCard` × 3, board behaviors × 3).
- Unit (backend): `cd backend && uv run pytest` — 4 tests pass (`/api/health`, health without static, frontend served, static asset).
- Manual: `bash scripts/start.sh` and visit `http://localhost:8000/` in a browser — Kanban board renders.
- E2E (frontend): `cd frontend && npm run test:e2e` against `npm run dev` on port 3100 — 3 tests pass (load board, add card, move card). Port 3100 was chosen to avoid conflicts with the user's portfolio on port 3000.

**Success criteria:**
- `docker build` succeeds.
- `docker run` → `GET /` renders the demo Kanban board with working drag and drop.
- All static assets load with 200 (verified for JS, CSS, and woff2 font).
- Color scheme decision is documented and applied.
- All tests pass (frontend + backend).

---

## Part 4: Fake user sign in

- [x] Backend:
  - Choose session strategy. For the MVP, simplest is a signed cookie containing the username (no DB session store). Document the choice in `backend/AGENTS.md`.
  - Add `POST /api/login` accepting `{username, password}` (JSON), validating `user`/`password`, setting an HttpOnly signed cookie.
  - Add `POST /api/logout` clearing the cookie.
  - Add `get_current_user` dependency that reads the cookie and returns the user, or raises 401.
  - Add `backend/tests/test_auth.py`:
    - Login success → 200 + `Set-Cookie`.
    - Login failure → 401.
    - Protected endpoint without cookie → 401.
    - Protected endpoint with cookie → 200.
    - Logout clears cookie.
  - Use a placeholder protected endpoint (e.g., `GET /api/whoami`) so tests have something to hit until Part 6.
- [x] Frontend:
  - Add `src/app/login/page.tsx` with a form (`username`, `password`, submit). For MVP, plain HTML form is fine; the API client posts JSON.
  - Add `src/lib/auth.ts` with `login()`, `logout()`, `getCurrentUser()` helpers.
  - Add `src/lib/api.ts` — typed fetch wrapper with `credentials: 'include'`.
  - Add `src/components/AuthGate.tsx` — client component that calls `getCurrentUser()` on mount; if missing, redirects to `/login`; otherwise renders children.
  - Wrap `<KanbanBoard />` in `AuthGate` from `src/app/page.tsx`.
  - Add a logout button to the Kanban board header (or its own header component).
- [x] Tests (frontend unit):
  - `AuthGate` redirects to `/login` when unauthenticated.
  - `AuthGate` renders children when authenticated (mock `getCurrentUser`).
  - Login page submits to the API and navigates to `/` on success.
- [x] Tests (Playwright, against `npm run dev`):
  - Visiting `/` when not logged in redirects to `/login`.
  - Submitting `user`/`password` lands on `/` and shows the Kanban board.
  - Logout returns to `/login`.

**Tests:** see substeps above.

**Success criteria:**
- First hit to `/` shows the login page (not Kanban).
- Logging in with `user`/`password` shows Kanban.
- Wrong credentials show an inline error.
- Logout button returns to `/login`.
- All unit, integration, and E2E tests pass.

---

## Part 5: Database modeling

> **Pause for user sign-off before continuing to Part 6.**

- [x] Choose ORM. Recommendation: **SQLAlchemy 2.x (sync)** for simplicity with SQLite + FastAPI. Document the choice in `backend/AGENTS.md`.
- [x] Design schema in `docs/SCHEMA.json` (machine-readable) with these tables and key fields:
  - `User`: `id` (pk), `username` (unique), `created_at`.
  - `Board`: `id` (pk), `user_id` (fk User), `title`, `created_at`. Unique constraint on `user_id` (one board per user for the MVP).
  - `Column`: `id` (pk), `board_id` (fk Board), `title`, `position` (int), `created_at`.
  - `Card`: `id` (pk), `column_id` (fk Column), `title`, `details`, `position` (int), `created_at`, `updated_at`.
- [x] Document the schema in `docs/DATABASE.md`:
  - ER description (text or mermaid).
  - Rationale per table.
  - How `position` orders items within a column (sparse integers optional; tight array on write is simplest for the MVP).
  - How the demo's 5 columns and 8 seed cards map to defaults.
  - Future-proofing notes (multi-board, real auth) without committing to them.
- [x] Get user sign-off.

**Tests:** N/A — design phase.

**Success criteria:**
- `docs/SCHEMA.json` exists and is valid JSON.
- `docs/DATABASE.md` explains the schema and rationale.
- Schema supports: multiple users, one board per user (current MVP), fixed columns with rename, editable cards with drag-and-drop ordering.
- User has approved the schema.

---

## Part 6: Backend

- [x] Add SQLAlchemy setup in `backend/app/database.py`:
  - Engine bound to `DATABASE_URL` (default `sqlite:///./data/pm.db`).
  - `SessionLocal` factory.
  - `Base` from `DeclarativeBase`.
  - `get_db` dependency for FastAPI.
  - On startup: `Base.metadata.create_all(engine)` (idempotent).
  - Create `data/` directory if missing.
- [x] Add models in `backend/app/models.py` matching `docs/SCHEMA.json`.
- [x] Add Pydantic schemas in `backend/app/schemas.py` (request/response DTOs).
- [x] Add seeding in `backend/app/seed.py` (called from startup if no users exist):
  - Create the default `user` account (no password needed for MVP — auth is hardcoded).
  - Create one board for that user.
  - Create the 5 default columns (`Backlog`, `Discovery`, `In Progress`, `Review`, `Done`).
  - Create the 8 seed cards matching the demo (mirror `initialData` in `frontend/src/lib/kanban.ts`).
- [x] Implement endpoints (all require auth via `get_current_user`):
  - `GET /api/board` — returns `{columns: [...], cards: {...}}` for the current user's board.
  - `PATCH /api/board` — body `{columns: [{id, title}]}` renames columns.
  - `POST /api/board/cards` — body `{column_id, title, details}` creates a card (appended to column).
  - `PATCH /api/board/cards/{id}` — body `{title?, details?}` updates a card.
  - `DELETE /api/board/cards/{id}` — deletes a card.
  - `POST /api/board/cards/{id}/move` — body `{column_id, position}` moves a card.
- [x] Tests in `backend/tests/`:
  - `test_db_init.py`: DB is created if missing; seed data is created on first run.
  - `test_board.py`: GET board returns full structure.
  - `test_columns.py`: rename works; only allowed columns are renamed.
  - `test_cards.py`: create, update, delete, move all work; positions update correctly.
  - `test_auth_required.py`: every endpoint returns 401 without a cookie.
  - Use `TestClient` + an ephemeral SQLite file in tmp (override `DATABASE_URL` via fixture).

**Tests:** see substeps above.

**Success criteria:**
- All endpoints implemented, typed, and tested.
- Auth required on all data endpoints.
- Database file persists across container restarts.
- Seed runs only on first run (idempotent).
- All tests pass.

---

## Part 7: Frontend + Backend

- [x] Replace frontend's in-memory data with API calls:
  - Update `src/lib/api.ts` with typed methods (`getBoard`, `renameColumns`, `createCard`, `updateCard`, `deleteCard`, `moveCard`).
  - Update `src/lib/kanban.ts` — keep types and `moveCard` helper, drop `initialData` (or keep as fallback only).
- [x] Update `KanbanBoard.tsx`:
  - Load board on mount via `getBoard()`.
  - On user actions, optimistically update local state and call the API; rollback on failure with an inline error.
  - Show a loading skeleton while fetching; show an error banner if the initial load fails.
- [x] Update login page wiring to call `POST /api/login` and persist the cookie.
- [x] Update logout button to call `POST /api/logout` and redirect to `/login`.
- [x] Tests:
  - Frontend unit (mock the API): board state transitions for add, edit, delete, move; rollback on failed API call.
  - Frontend E2E (Playwright) against `npm run dev` with a mocked or local backend:
    - Login flow.
    - Load board.
    - Add, edit, delete, move a card.
    - Logout.
  - Backend tests still pass.

**Tests:** see substeps above.

**Success criteria:**
- Kanban board is fully persistent across reloads.
- All user actions sync to the backend.
- Optimistic UI with rollback on API failure.
- Loading + error states are visible.
- All tests pass (frontend + backend).

---

## Part 8: AI connectivity

> **Pause for user sign-off before continuing to Part 9.**

**User decisions:**
- Docker `scripts/start.sh` will pass `--env-file .env` so the container picks up `.env` for local runs.
- `.env` created with `OPENROUTER_API_KEY=sk-or-v1-e9fff...` (placeholder key; replace with real key for actual AI calls).

- [ ] Add `openai>=1.x` to backend deps (OpenRouter is OpenAI-compatible).
- [ ] Document required env in `backend/AGENTS.md`:
  - `OPENROUTER_API_KEY` — required at runtime.
  - `.env` in project root holds it for local runs.
  - For Docker, pass via `--env-file` in `scripts/start.sh` (or document env-file usage).
- [ ] Create `backend/app/services/__init__.py` and `backend/app/services/ai.py`:
  - Client: `openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)`.
  - Constants: `PRIMARY_MODEL = "openai/gpt-oss-120b"`, `FALLBACK_MODEL = "openai/gpt-oss-20b"`.
  - `call_ai(messages) -> str`: try primary; on any exception (timeout, 5xx, model-not-available), try fallback. Return the response text.
- [ ] Add `POST /api/ai/test`:
  - Hardcoded message: `[{"role": "user", "content": "What is 2+2?"}]`.
  - Returns the AI response text.
- [ ] Tests:
  - Unit: mock the OpenAI client to return a primary response; assert `call_ai` returns it without calling fallback.
  - Unit: mock primary to raise; assert fallback is called and its response is returned.
  - Integration (real API): if `OPENROUTER_API_KEY` is set in the test env, call `POST /api/ai/test` and assert the response contains `"4"`. Skip otherwise with a clear message.

**Tests:** see substeps above.

**Success criteria:**
- `POST /api/ai/test` returns a response containing `"4"` for the prompt "What is 2+2?".
- When the primary model fails (any reason), the fallback model is used.
- API key is loaded from environment, never hardcoded.
- All tests pass.

---

## Part 9: AI with Kanban context

- [x] Define request/response schemas in `backend/app/schemas.py`:
  - Request: `AIChatRequest { message: str, conversation_history: list[Message] | None }`.
  - Response: `AIChatResponse { response: str, board_update: BoardUpdate | None, board: BoardData }`.
  - `BoardUpdate.operations: list[Operation]` where `Operation` is a tagged union:
    - `create_card { column_id: str, title: str, details: str }`.
    - `update_card { card_id: str, title?: str, details?: str }`.
    - `delete_card { card_id: str }`.
    - `move_card { card_id: str, column_id: str, position: int }`.
    - `rename_column { column_id: str, title: str }`.
  - Validate with Pydantic discriminated union.
- [x] Implement `POST /api/ai/chat`:
  - Require auth.
  - Load the current board for the user.
  - Build system prompt containing: the user's role, the current board JSON, the operations schema, and instructions ("respond with JSON matching this schema").
  - Call `call_ai` with `response_format={"type": "json_schema", ...}` (OpenRouter supports OpenAI-style structured outputs).
  - Parse and validate response against `AIChatResponse`.
  - If `board_update` is present, apply operations in a single transaction:
    - For each operation, perform the corresponding DB action.
    - Validate preconditions (card exists, column exists, belongs to the user) and reject the whole update if any op is invalid.
  - Return `{response, board_update, board}` (latest board state).
- [x] Tests:
  - Unit: mock `call_ai` to return chat-only response → no DB writes, response returned.
  - Unit: mock to return a valid `create_card` op → card created with correct column/position.
  - Unit: mock to return an invalid op (e.g., unknown `card_id`) → entire update rejected, no DB writes.
  - Unit: conversation history is included in the messages sent to the AI.
  - Integration (real API, deterministic prompt): prompt "Create a card titled 'Smoke test card' in the Backlog column." → verify the card exists afterward.

**Tests:** see substeps above.

**Success criteria:**
- [x] AI can answer questions about the board without mutating it.
- [x] AI can mutate the board via structured output; mutations are validated and applied atomically.
- [x] Conversation history is threaded across calls.
- [x] All tests pass.
- All tests pass.

---

## Part 10: AI chat UI

- [ ] Build chat UI:
  - `src/components/ChatSidebar.tsx` — collapsible sidebar; controlled by parent.
  - `src/components/ChatMessage.tsx` — message bubble (user vs AI).
  - `src/components/ChatInput.tsx` — textarea + send button.
  - `src/lib/chat.ts` — typed client for `POST /api/ai/chat`; local state for message history.
- [ ] Add a chat toggle button to the Kanban board header.
- [ ] Wire up:
  - On send, POST to `/api/ai/chat` with the current message and history.
  - Append user + AI messages to local history.
  - If the response includes `board_update`, refresh the Kanban state (call `getBoard()` again, or merge locally — pick the simpler option).
  - Show a typing indicator while waiting.
  - Show inline errors on failure.
- [ ] Tests:
  - Frontend unit: `ChatInput` submits, `ChatMessage` renders, sidebar open/close state.
  - Frontend E2E (Playwright): open chat → send "create a card titled E2E card in Backlog" → AI responds → board shows the new card.

**Tests:** see substeps above.

**Success criteria:**
- A polished, responsive sidebar chat widget is present.
- The AI can update the Kanban via chat.
- The board refreshes automatically when the AI changes it.
- All tests pass.