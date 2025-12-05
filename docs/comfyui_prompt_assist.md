# ComfyUI Prompt Assist Node

This repository includes a custom ComfyUI node that rewrites or safety-checks prompts using the OpenAI Python client. The node automatically falls back to offline passthrough when an API key is not configured.

## Installation
1. Copy the `comfyui_nodes` folder (or just `comfyui_nodes/prompt_assist.py`) into your ComfyUI `custom_nodes` directory.
2. Restart ComfyUI so it discovers the new node.
3. (Optional) Add an `.env` file in your ComfyUI root with:

   ```env
   OPENAI_API_KEY=sk-...
   ```

   Without the key, the node returns the original prompt unchanged.

## Node settings
- **mode**: `rewrite` (default) to polish the prompt or `safety_check` to validate and return a safe variant.
- **model**: OpenAI Responses model name, e.g., `gpt-4o-mini`.
- **max_output_tokens**: Cap on the rewritten or safety output.
- **rate_limit_per_minute**: Lightweight client-side limiter to avoid flooding the API.
- **bypass_online**: Force offline passthrough, even when a key is present.

Validation errors (empty prompts, missing JSON in safety mode, exceeding the rate limit, etc.) are raised directly by the node so they appear in the ComfyUI UI.

## Example workflow wiring
A minimal text-to-image flow that uses the assist node for prompt hygiene:

1. **Text**: Enter the user prompt.
2. **Prompt Assist (OpenAI)**: Set `mode` to `rewrite` or `safety_check`. Connect the `Text` output to the node's `prompt` input.
3. **CLIP Text Encode**: Feed the `prompt` output from the assist node into your text encoder.
4. **KSampler / Sampler**: Use the encoded conditioning as usual.
5. **VAE Decode / Save Image**: Complete the pipeline.

When no `OPENAI_API_KEY` is set (or `bypass_online` is enabled), the assist node returns the original text and notes the bypass in its status output. With an API key configured, the node calls `responses.create()` for rewriting or safety checking before handing the text to downstream nodes.
