# ComfyUI + Z-Image Art Generation System Plan

## Objectives
- Deliver an offline-capable art generation tool built on ComfyUI with Z-Image pipelines (including Z-Image Turbo for fast previews).
- Keep all components reproducible with Git versioning and GitHub CI for automated validation of workflows and nodes.
- Provide clear operator and contributor guidance for setup, maintenance, and performance tuning.

## Architecture overview
- **Runtime:** ComfyUI running locally (Docker or bare-metal) with Z-Image custom nodes; optional ControlNet and upscalers.
- **Interface:** ComfyUI web UI plus a thin API facade (FastAPI/Flask) to expose `generate_art` for bots or external tools.
- **Storage:** Local model cache mounted into ComfyUI container/host; Git repo for workflow JSON templates and automation scripts.
- **Automation:** GitHub Actions for linting workflow JSON, validating node availability, and building/publishing container images.
- **Security:** Local-only default; optional API token if remote exposure is required. Keep model downloads hashed/verified.

## ComfyUI + Z-Image setup
1. **Dependencies:** Python 3.10+, Git, GPU drivers (CUDA/ROCm/Metal). For Docker: compose v2.
2. **Install ComfyUI:**
   ```bash
   git clone https://github.com/comfyanonymous/ComfyUI.git
   cd ComfyUI && python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Add Z-Image nodes:**
   ```bash
   cd custom_nodes
   git clone https://github.com/Z-Engine-Labs/ComfyUI-Z-Image.git
   # For Turbo variant
   git clone https://github.com/Z-Engine-Labs/ComfyUI-Z-Image-Turbo.git
   ```
4. **Model placement:**
   - Base SD checkpoints (e.g., SDXL/SD1.5) in `models/checkpoints/`.
   - Z-Image model files per repository instructions (keep SHA256 checks).
5. **Launch:** `python main.py --listen 0.0.0.0 --port 8188`
6. **Docker option:** Build an image that layers ComfyUI + Z-Image nodes with a mounted `/models` volume for checkpoints and embeddings.

## Workflow design (Z-Image)
- **Text-to-Image default:** Prompt → CLIP encode → Z-Image UNet → VAE decode → safety filter (optional) → output.
- **Turbo preview path:** Swap to Z-Image Turbo node with reduced steps/CFG for quick drafts.
- **Control paths:** Add ControlNet (depth/canny/pose) branches to condition prompts while keeping Z-Image as primary denoiser.
- **Image-to-Image:** Use `KSampler` strength controls with initial image input; reuse Z-Image UNet.
- **Metadata:** Persist seeds, CFG, scheduler, checkpoint hash, and node graph version into PNG metadata for reproducibility.

## API bridge for bots/tools
- Wrap ComfyUI’s `/prompt` endpoint with a small service exposing `POST /generate_art` that:
  - Accepts: prompt, negative prompt, width/height, steps, CFG, sampler, seed, model id, control images.
  - Translates requests into ComfyUI workflow JSON (selects Z-Image or Turbo graph), submits job, polls `/history` for status.
  - Streams progress or returns signed URLs/paths of outputs. Apply prompt filtering before submission if needed.
- Provide SDK snippets (Python/TypeScript) in the repo for bot integrations.

## GitHub integration and automation
- **Repo layout:**
  - `/workflows/`: curated ComfyUI JSON graphs (Z-Image standard, Turbo fast, ControlNet variants).
  - `/scripts/`: setup, model download/checksum, and API bridge launcher.
  - `/docker/`: Dockerfile/compose for ComfyUI + Z-Image + API facade.
  - `/ci/`: schema checks and smoke tests.
- **GitHub Actions:**
  - Validate workflow JSON against ComfyUI schema; ensure required custom nodes are referenced.
  - Run `ruff`/`mypy`/`pytest` for API bridge and scripts.
  - Optional nightly container build pushing to GHCR with cache mounts for model layers.
- **Release process:** Tag versions when workflow templates change; attach checksums for model packs; publish changelog and upgrade notes.

## Performance & efficiency tips
- Prefer fp16/bf16 where supported; enable xformers/flash attention on NVIDIA to reduce VRAM.
- Provide presets (fast/quality/batch) that swap schedulers and step counts.
- Cache ControlNet and VAE models separately to avoid duplicating downloads.
- Enable tiled VAE for high-resolution outputs; document VRAM thresholds.
- Benchmark CPU-only fallbacks with Z-Image Turbo at reduced resolution for low-spec systems.

## Roadmap (ComfyUI + Z-Image)
- **M1:** Base ComfyUI setup, Z-Image + Turbo nodes installed, baseline text-to-image workflow, Docker/compose, API bridge skeleton.
- **M2:** ControlNet and image-to-image workflows, model checksum/downloader script, prompt metadata persistence, basic CI (lint/tests).
- **M3:** Performance tuning (xformers/flash attention, tiled VAE), batch queueing in API bridge, SDK samples, nightly container builds.
- **M4:** Advanced UX (preset packs, safety filters, web onboarding), plugin registry for custom nodes, automated regression image tests with fixed seeds.

## Operator checklist
- Verify GPU drivers before first launch; run a smoke test prompt via Z-Image Turbo.
- Keep `custom_nodes` up to date; pin commits in `requirements.lock`/`compose` to avoid breaking changes.
- Monitor disk usage in `models/` and clear unused checkpoints; maintain checksum manifest in Git.
- When exposing remotely, front the API with HTTPS + token auth; keep ComfyUI UI access limited or behind a VPN.
