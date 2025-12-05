# ComfyUI Workspace

This directory contains a self-contained ComfyUI setup that lives alongside the OpenAI Python client library. The ComfyUI assets are intentionally isolated from the `openai` package code so the two workflows remain independent.

## Architecture overview

- `docker/`: Dockerfiles, compose snippets, and runtime configs for building container images.
- `workflows/`: Example ComfyUI workflows that can be mounted or imported at runtime.
- `scripts/`: Helper scripts for container operations, model management, or CI tasks.
- `models/`: A mount point for model artifacts. Only manifests and metadata are checked into Git; actual model binaries should be placed in the mounted `/models` volume.
- `ci/`: Continuous integration helpers specific to the ComfyUI environment.

## Prerequisites

- Docker 24+ with access to the NVIDIA Container Toolkit if you plan to use GPU acceleration.
- Docker Compose (v2) installed and available as `docker compose`.
- A writable host directory that can be mounted to `/models` for large model files.

## Running with Docker

Build and run a single container, mounting your host models directory:

```sh
docker build -t local/comfyui -f comfyui/docker/Dockerfile .
docker run --rm -p 8188:8188 \
  -v $(pwd)/comfyui/models:/app/models \
  -v /path/to/host/models:/models:ro \
  local/comfyui
```

Replace `/path/to/host/models` with the directory that contains your downloaded model files.

## Running with Docker Compose

A compose file is provided at the repository root. To start ComfyUI with the `/models` volume mounted:

```sh
docker compose -f compose.yaml up --build
```

By default the compose file expects a host directory bound to `/models`. You can override the path with an environment variable in a `.env` file, for example:

```
COMFYUI_MODELS=/absolute/path/to/your/models
```

Place this file next to `compose.yaml` before running compose. The container will mount `COMFYUI_MODELS` to `/models` and reuse `comfyui/models` for checked-in metadata such as `checksums.md`.

## Model management

Large models should **not** be committed to the repository. Use the `/models` volume for the binaries and track checksums in `models/checksums.md` to document what has been downloaded and verified.
