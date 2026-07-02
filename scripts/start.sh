#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker build -t pm-app .
docker run -d --name pm-app -p 8000:8000 pm-app

echo "Started pm-app on http://localhost:8000"
