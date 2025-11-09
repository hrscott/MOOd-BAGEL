#!/usr/bin/env python3
"""Example entrypoint for the BAGEL GPU workflow."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a ColabDesign + MPNN + AF demo workflow")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(os.environ.get("INPUT_DIR", "/workspace/input")) / "payload.json",
        help="Path to the input payload JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(os.environ.get("RESULTS_DIR", "/workspace/results")) / "outputs.json",
        help="Path for writing the workflow output JSON file.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Input payload not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_demo(payload: dict) -> dict:
    """Mock implementation that echoes metadata."""
    return {
        "status": "success",
        "input_keys": sorted(payload.keys()),
        "notes": "This is a placeholder implementation for the vendored GPU workflow.",
    }


def main() -> None:
    args = parse_args()
    payload = load_payload(args.input)
    result = run_demo(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    print(f"[colabdesign-demo] Wrote results to {args.output}")


if __name__ == "__main__":
    main()
