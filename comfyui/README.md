# ComfyUI Stack

This directory provisions a standalone ComfyUI stack with Z-Image utilities, reusable workflows, and CI helpers for schema checks and smoke renders.

## Directory layout
- `workflows/`: Store ComfyUI JSON graphs (exported from the UI) for repeatable pipelines.
- `docker/`: Docker image and compose file for ComfyUI + Z-Image with host-mounted model storage.
- `scripts/`: Helper utilities (model downloader with checksums, API facade launcher).
- `ci/`: Linting and smoke-render entry points for CI.

## Requirements
- **GPU**: CUDA-capable GPU with at least 8–12 GB VRAM for SDXL-class workflows. Install the NVIDIA Container Toolkit on the host so Docker can access the GPU.
- **CPU fallback**: CPU-only runs are possible by omitting GPU flags, but renders will be dramatically slower and some custom nodes may expect CUDA.
- **Disk**: Allocate tens of GB for model checkpoints and embeddings. The compose file mounts `../models` into the container by default.
- **Host tools**: Docker 24+ and Docker Compose (Plugin or V2). Git is required if you plan to build the image locally with custom nodes.

## Running locally
1. Create a models directory adjacent to this repo (or adjust the `COMFYUI_MODELS_DIR` env var used in `docker/docker-compose.yaml`).
2. (Optional) Fetch models with the downloader script:
   ```bash
   ./scripts/download_models.sh
   ```
3. Build and start the stack (GPU-enabled by default):
   ```bash
   cd docker
   COMFYUI_MODELS_DIR=../models docker compose up --build
   ```
   - Add `COMFYUI_TAG=<version>` to pin a specific ComfyUI base image.
   - Remove the `deploy.resources.reservations` block or set `USE_GPU=0` in the compose environment to run CPU-only.
4. Access the UI at http://localhost:8188 and drop workflow JSON files from `workflows/` as needed.

## Notes
- The image installs the Z-Image utilities under `custom_nodes/` during build.
- CI helpers assume workflows are valid JSON and render a minimal smoke image for break-glass verification; see `ci/README.md` for guidance.
