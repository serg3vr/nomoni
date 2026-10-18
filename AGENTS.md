# AGENTS.md

Personal finance tracker monorepo. `back/api` = FastAPI + SQLAlchemy 2.0 (async) + Alembic, targets PostgreSQL. `front/web` = Quasar v2 (Vue 3 + TS + Pinia). `MVP.md` (Spanish, gitignored) is the product spec; design decisions D1–D19 live there and are binding.

## File/directory quirks

- `docker-compose.yml`, `docker/Dockerfile`, and `back/api/.env` are gitignored on purpose; the tracked templates are `docker-compose.yml.dist`, `docker/Dockerfile.dist`, and `back/api/.env.dist`. Change the `.dist` template, not just the local copy. Same applies to `MVP.md` (gitignored local spec — it exists anyway).
- No CI configured (`.github` is empty). Verification is manual: pytest for backend, lint + typecheck for frontend.

## Backend (`back/api`)

- Config is **fail-fast from `.env`** (`app/core/config.py`): copy `.env.dist` → `.env` first. `DATABASE_URL` and `JWT_SECRET` are required; nothing starts without them. Backend runs on port 8000.
- Run tests without any database: `cd back/api && pytest` — `tests/conftest.py` overrides `get_db` with in-memory SQLite, so no Postgres and no Alembic needed. Single file: `pytest tests/test_auth.py`.
- Alembic: `cd back/api && alembic upgrade head`. It reads `MIGRATION_DATABASE_URL` (DDL user) first and falls back to `DATABASE_URL` (CRUD-only, no-DDL user). Two-user pattern is intentional — after each migration the DDL user grants the app user access.
- Postgres is **not** containerized in the tracked compose (host DB via `host.docker.internal`). `docker compose up` from the repo root starts only the API; it mounts `./back/api` with uvicorn `--reload`, so edits hot-reload.
- Layered structure: `routers/` → `services/` → `repositories/` → `models/`. Keep new endpoints in that pattern.
- **`user_id` always comes from the JWT `sub`** (`deps.get_current_user`) — never accept it from the client. Tenancy is enforced by composite FKs `(user_id, id)`; touching another user's resource must return 404, not 403.
- Money is **integer cents** everywhere (`bigint` in DB, number in TS) — never float; amount is the only required field on a transaction, and the transaction type lives in its category (no `type` column).
- System-seeded rows (`is_system=true`, categories/wallets seeded at registration) must 403 on DELETE — they can only be renamed or hidden.
- IDs are UUIDv7 (`uuid7` from the `uuid6` package), not UUIDv4.
- API routes have **no `/api` prefix** on the server (`/auth`, `/categories`, `/wallets`, `/transactions`, `/health`). MVP.md says `/api/v1`; trust the code. The `/api` prefix exists only client-side (see below).

## Frontend (`front/web`)

- Commands: `npm install`, `npm run dev` (port 9000 — that's also why `CORS_ORIGINS` defaults to `http://localhost:9000`), `npm run build`. Verify with `npm run lint:check` then `npm run typecheck`; to fix formatting/lint use `npm run lint` (oxfmt + oxlint — **not** eslint/prettier).
- Routing is **file-based** (`filenameBasedRouting: true`, `vue-router/auto-routes`): a page under `src/pages/auth/login.vue` is route `/auth/login`. `src/router/typed-router.d.ts` is generated — don't hand-edit.
- The dev server proxies `/api/*` to `localhost:8000` and **strips the `/api` prefix**; axios `baseURL` defaults to `/api` (`VITE_API_URL` to override). So frontend code calls `/api/transactions`, the backend sees `/transactions`.
- Auth token lives in `localStorage["nomoni_token"]`; a router guard and an axios 401 interceptor both redirect to `/auth/login`.
- Dashboard aggregates (totals/breakdowns) are computed client-side from transaction lists — there is deliberately no aggregation endpoint (D15).
- Lint/typecheck configs live at `front/web/oxlint.config.ts`, `oxfmt.config.ts`, `tsconfig.json`.
