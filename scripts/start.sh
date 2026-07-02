#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

IMAGE_NAME="pm-app"
CONTAINER_NAME="pm-app"
HOST_PORT=8000

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null
fi

docker build -t "$IMAGE_NAME" .
docker run -d --name "$CONTAINER_NAME" -p "${HOST_PORT}:8000" "$IMAGE_NAME"

for _ in $(seq 1 30); do
  if curl -sf "http://localhost:${HOST_PORT}/api/health" >/dev/null 2>&1; then
    echo "Started $CONTAINER_NAME on http://localhost:${HOST_PORT}"
    exit 0
  fi
  sleep 0.5
done

echo "ERROR: $CONTAINER_NAME did not become ready within 15s" >&2
exit 1
