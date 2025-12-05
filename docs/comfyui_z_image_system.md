# ComfyUI + Z-Image Art Generation System Plan

## Objectives
- Deliver an offline-capable art generation tool built on ComfyUI with Z-Image pipelines (including Z-Image Turbo for fast previews).
- Ship specialized creative tools: Face Transpose, Image Clean Up, Scene + Model Blend, Environment Generation, Character Model Generation, and a Final Render finisher (clean, professional polish).
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

## Specialized tool workflows
- **Face Transpose:** Face-detection node → landmark/pose extraction → warp source face to target pose → Z-Image img2img refinement with high face fidelity (use `FaceID` or InsightFace embeddings for identity lock) → optional inpainting around seams. Provide presets for neutral ↔ dynamic angles and batch retargeting.
- **Image Clean Up:** Segment foreground/background → mask defects with brush/auto-mask → inpaint using Z-Image (low CFG, higher denoise) → optional ESRGAN/TV denoise pass. Include "artifact scrub" preset (JPEG cleanup) and "line repair" preset (thin-line restoration).
- **Scene + Model Blend:** Dual encoders (scene prompt + character prompt) feeding a Blend/LatentMix node → Z-Image sampler with weighted condition controls → light pass ControlNet depth for coherence. Include sliders for scene/model ratio and a seed-lock option for iteration stability.
- **Environment Generation:** Environment prompt → optional reference depth/skybox → tiled VAE + ControlNet depth → Z-Image sampler tuned for wide aspect ratios. Provide presets for interior/exterior and day/night lighting, plus a panorama stitching helper.
- **Character Model Generation:** Character prompt + identity embeddings → Z-Image sampler with low denoise seed lock → pass through LoRA loader for style/wardrobe → save checkpoint/LoRA metadata for reuse. Offer a "cast management" JSON manifest to track identities, outfits, and seeds.
- **Final Render Polish:** Take draft render → high-resolution upscaling (ESRGAN/Latent upscaler) → color balance/levels node → subtle sharpen → compress-safe export (TIFF/PNG). Add watermark toggle and layered export (mask + alpha) for downstream design tools.

## Layering guide (JP reference translated & applied)
- **What the JP guide shows (translated):**
  - Keep a consistent PSD layer stack: top accents (sparkles, screen/overlay flares), global adjustment layers (gradient maps/LUTs/level tweaks), "add" layers for highlights, "multiply" layers for shadows and AO, then clipped base-color groups (skin, hair, glasses, clothes, background) each with line-art and fill separated. Masks isolate hair/skin overlap, and there are per-part shadow/highlight sublayers. Background gradients and rim-light overlays sit just above the background fill. Notes emphasize checking color harmony per layer and keeping RGB/HSV ranges controlled.
  - Practical tips called out: avoid flattening early; name layers clearly; keep high-saturation accent colors on their own overlay layer; use clipping masks to prevent color spill; preserve the line-art atop fills; group FX (glow, noise, blur) above everything; run final checks on level balance and AO depth.
- **How we map this into ComfyUI workflows:**
  - Build node groups mirroring the stack: base-color fills via segmented masks → AO/multiply pass (using custom AO node or shadow ControlNet) → highlight/add pass → overlay/gradient-map adjustment → FX (glow/noise) → export with separated RGBA/mask outputs. Save masks per part to reuse across Face Transpose, Clean Up, and Final Render flows.
  - Expose sliders for layer weights (multiply/add/overlay strength) and color-harmony presets (HSV clamp) so operators can match the JP guide’s discipline while staying procedural.

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
  - Include smoke renders for each specialized tool workflow (Face Transpose, Clean Up, Blend, Environment, Character, Final Render) using small seed fixtures to prevent regressions.
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
