#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<USAGE
Run the BAGEL GPU workflow.

Usage:
  ${BASH_SOURCE[0]} [--detach]

Options:
  --detach    Run the workflow in detached mode.
USAGE
}

DETACH_FLAG=""
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      usage
      exit 0
      ;;
    --detach)
      DETACH_FLAG="--detach"
      shift
      ;;
    *)
      echo "Unknown option: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

"${SCRIPT_DIR}/gpu_preflight.sh"

echo "[pipeline] Launching workflow..."
docker compose \
  -f "${SCRIPT_DIR}/docker/compose.yaml" \
  up ${DETACH_FLAG}
