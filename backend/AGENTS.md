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
  tests/
    __init__.py
    test_health.py
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
