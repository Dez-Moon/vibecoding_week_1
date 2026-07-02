#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="pm-app"

if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker stop "$CONTAINER_NAME"
  docker rm "$CONTAINER_NAME"
  echo "Stopped and removed $CONTAINER_NAME"
else
  echo "$CONTAINER_NAME is not running"
fi