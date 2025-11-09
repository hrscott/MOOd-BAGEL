#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_FILE="${1:-${SCRIPT_DIR}/../artifacts/host_env.txt}"

mkdir -p "$(dirname "${OUTPUT_FILE}")"

echo "[capture-env] Writing host environment report to ${OUTPUT_FILE}" \
  | tee "${OUTPUT_FILE}"

{
  echo "# Host Environment Report"
  echo
  echo "## Docker"
  docker version
  echo
  echo "## NVIDIA SMI"
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi not available"
  fi
  echo
  echo "## GPU Workflow Variables"
  env | grep -E 'RESULTS_DIR|INPUT_DIR|MODEL_CACHE' || true
} >>"${OUTPUT_FILE}"

echo "[capture-env] Done." >>"${OUTPUT_FILE}"
