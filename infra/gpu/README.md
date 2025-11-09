# GPU Workflow Backend

This directory vendors the GPU workflow that BAGEL uses to provision a ColabDesign-based backend.
It contains Docker definitions, orchestration scripts, and documentation required to bootstrap a GPU-enabled pipeline in a reproducible way.

## Layout

- `bootstrap.sh` – prepares host dependencies, validates prerequisites, and pulls the Docker images required for the workflow.
- `gpu_preflight.sh` – performs environment checks to ensure a CUDA-capable GPU and supporting drivers are available.
- `run_pipeline.sh` – orchestrates the end-to-end workflow using Docker Compose.
- `docker/` – Dockerfiles, Compose definitions, and runtime code for ColabDesign.
- `scripts/` – helper utilities for capturing environment details and launching interactive shells inside the ColabDesign container.
- `docs/` – additional documentation, including a quickstart guide for running the workflow.

See `docs/QUICKSTART.md` for usage instructions.
