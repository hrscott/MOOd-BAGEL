#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<USAGE
Bootstrap the BAGEL GPU workflow.

Usage:
  ${BASH_SOURCE[0]} [--no-cache]

Options:
  --no-cache    Skip using cached Docker layers when building images.
USAGE
}

NO_CACHE=0
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      usage
      exit 0
      ;;
    --no-cache)
      NO_CACHE=1
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

BUILD_ARGS=(--pull)
if [[ ${NO_CACHE} -eq 1 ]]; then
  BUILD_ARGS+=(--no-cache)
fi

echo "[bootstrap] Building ColabDesign GPU image..."
docker compose \
  -f "${SCRIPT_DIR}/docker/compose.yaml" \
  build "${BUILD_ARGS[@]}" colabdesign

echo "[bootstrap] GPU workflow bootstrapped successfully."
