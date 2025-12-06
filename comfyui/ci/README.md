# CI Helpers

These scripts keep ComfyUI workflows linted and boot the stack for smoke renders.

- `lint_workflows.sh`: Validates that every `*.json` file under `workflows/` is parseable JSON.
- `smoke_render.sh`: Builds/starts the docker compose stack, waits for the UI to respond on port 8188, and exits non-zero if startup fails.

Run locally from the repo root:
```bash
./comfyui/ci/lint_workflows.sh
./comfyui/ci/smoke_render.sh
```
