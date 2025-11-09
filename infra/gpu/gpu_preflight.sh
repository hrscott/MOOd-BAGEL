#!/usr/bin/env bash
set -euo pipefail

check_command() {
  local cmd=$1
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[preflight] Required command '$cmd' is not available." >&2
    exit 1
  fi
}

echo "[preflight] Checking host prerequisites..."

check_command docker

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[preflight] Detected NVIDIA driver:"
  nvidia-smi
else
  echo "[preflight] Warning: 'nvidia-smi' not found. GPU access may be unavailable." >&2
fi

echo "[preflight] Preflight checks completed."
