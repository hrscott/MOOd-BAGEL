#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${SCRIPT_DIR}/../docker/compose.yaml"

SERVICE=${1:-colabdesign}

if ! docker compose -f "${COMPOSE_FILE}" ps "${SERVICE}" >/dev/null 2>&1; then
  echo "[colabdesign-shell] Bringing up ${SERVICE} container..."
  docker compose -f "${COMPOSE_FILE}" up -d "${SERVICE}"
fi

docker compose -f "${COMPOSE_FILE}" exec "${SERVICE}" /bin/bash
