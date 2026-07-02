# Backend

FastAPI backend, packaged with uv, served from a Docker container. This file documents the layout, runtime decisions, and how to run/test.

## Decisions

- Python 3.13
- FastAPI + Uvicorn (latest stable)
- Package manager: uv
- Host port: 8000
- Container name: `pm-app`
- Image tag: `pm-app`

## Layout

```
backend/
  pyproject.toml        # uv-managed project + deps
  app/
    __init__.py
    main.py             # FastAPI app, routes
    auth.py             # Session cookie sign/verify, get_current_user dependency
  tests/
    __init__.py
    conftest.py         # Sets SECRET_KEY for deterministic signing
    test_health.py
    test_frontend.py
    test_auth.py
```

`uv run` is used everywhere (not bare `python` or `pytest`) so the venv is consistent.

## Run locally (without Docker)

```
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Test

```
cd backend
uv run pytest
```

## Run in Docker

Use the `scripts/` directory: `bash scripts/start.sh` builds the image and runs the container detached, mapping host port 8000 to container port 8000. `bash scripts/stop.sh` stops and removes it.

## Session strategy

- Signed cookie via `itsdangerous.URLSafeSerializer` (HMAC SHA-256). Payload is `{"username": ...}`; cookie name `pm_session`.
- No database-backed session store; the cookie is the entire session.
- For the MVP, the only valid credential is `user` / `password`. Real auth lands in a later part.
- Signing key is `SECRET_KEY` (env var). When unset, the app logs a warning and uses the insecure dev fallback `"dev-only-secret"`. Set `SECRET_KEY` in production.
- Cookie attributes: `HttpOnly`, `SameSite=Lax`, `Path=/`. `Secure` is omitted so local HTTP works; flip it on once a TLS terminator is in front.
- `SameSite=Lax` is sufficient across `127.0.0.1:3100` (next dev) and `127.0.0.1:8000` (uvicorn) because they share a registrable domain per RFC 6265bis — i.e., same-site even though cross-origin.
- CORS is open to `http://127.0.0.1:3100` and `http://localhost:3100` with `allow_credentials=True`, so the dev frontend can hit the API cross-origin. In production (static export served by FastAPI on the same origin), CORS is a no-op.
