#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".env" ]]; then
  cp .env.example .env
fi

cleanup() {
  if [[ "${KEEP_CONTAINERS:-0}" != "1" ]]; then
    docker compose down >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

docker compose up --build -d mongodb neo4j minio jaeger

export RUN_REAL_E2E=1
python3 -m pytest -m real_e2e -o addopts=''

