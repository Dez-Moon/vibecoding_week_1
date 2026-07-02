# syntax=docker/dockerfile:1.7

# Stage 1: Build the frontend static export
FROM node:22-slim AS frontend-builder
WORKDIR /build

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Backend with the built frontend served as static files
FROM python:3.13-slim

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/pyproject.toml ./
RUN uv sync --no-install-project --no-dev

COPY backend/app ./app
RUN uv sync --no-dev

COPY --from=frontend-builder /build/out /app/static

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
