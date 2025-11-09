# GPU Workflow Quickstart

This guide explains how to run the vendored GPU workflow locally.

## Prerequisites

- Docker with NVIDIA Container Toolkit configured for GPU passthrough.
- Access to a CUDA-capable GPU with recent drivers.
- `docker compose` plugin (v2+).

## Setup

1. Copy `infra/gpu/docker/.env.example` to `infra/gpu/docker/.env` and update the variables to match your environment.
2. Run the bootstrap script to build the ColabDesign image:

   ```bash
   ./infra/gpu/bootstrap.sh
   ```

3. (Optional) Capture environment information for reproducibility:

   ```bash
   ./infra/gpu/scripts/capture_env.sh
   ```

## Running the Pipeline

Start the workflow using Docker Compose:

```bash
./infra/gpu/run_pipeline.sh
```

Use `--detach` if you prefer the services to run in the background.

To open an interactive ColabDesign shell within the running container:

```bash
./infra/gpu/scripts/colabdesign_shell.sh
```

## Stopping the Workflow

If running in detached mode, stop the stack with:

```bash
cd infra/gpu && docker compose -f docker/compose.yaml down
```

## Troubleshooting

- Re-run `gpu_preflight.sh` to verify Docker and GPU availability.
- Use `docker compose logs` to inspect service output.
