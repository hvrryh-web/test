from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Callable, Tuple

from openai import OpenAI


@dataclass
class _RateLimiter:
    per_minute: int
    window_start: float = time.time()
    calls: int = 0

    def check(self) -> None:
        now = time.time()
        if now - self.window_start >= 60:
            self.window_start = now
            self.calls = 0
        if self.calls >= self.per_minute:
            raise ValueError(
                f"Rate limit of {self.per_minute} calls/minute reached. Wait or lower rate_limit_per_minute."
            )
        self.calls += 1


class PromptAssistNode:
    """
    ComfyUI node that rewrites or validates prompts using OpenAI Responses API.

    The node can operate in offline passthrough mode when no API key is available
    or when bypass_online is set to True.
    """

    CATEGORY = "OpenAI/Assist"
    FUNCTION = "assist"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "status")

    def __init__(self, client_factory: Callable[[], OpenAI] | None = None):
        self._client_factory = client_factory or self._default_client_factory
        self._limiter = None

    @classmethod
    def INPUT_TYPES(cls):  # pragma: no cover - ComfyUI inspects this
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
            },
            "optional": {
                "mode": (["rewrite", "safety_check"], {"default": "rewrite"}),
                "instructions": (
                    "STRING",
                    {
                        "default": "Rewrite the user prompt for clarity while preserving intent and safety.",
                        "multiline": True,
                    },
                ),
                "model": (
                    "STRING",
                    {
                        "default": "gpt-4o-mini",
                        "multiline": False,
                    },
                ),
                "max_output_tokens": ("INT", {"default": 200, "min": 1, "max": 2048}),
                "rate_limit_per_minute": ("INT", {"default": 30, "min": 1, "max": 120}),
                "bypass_online": ("BOOLEAN", {"default": False}),
            },
        }

    @staticmethod
    def _default_client_factory() -> OpenAI:
        return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def _validate_inputs(
        self, prompt: str, model: str, max_output_tokens: int, rate_limit_per_minute: int
    ) -> None:
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")
        if not model or not model.strip():
            raise ValueError("model cannot be empty")
        if max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        if rate_limit_per_minute <= 0:
            raise ValueError("rate_limit_per_minute must be positive")

    def _should_bypass(self, bypass_online: bool) -> Tuple[bool, str]:
        if bypass_online:
            return True, "Bypass requested; returned prompt unchanged."
        if not os.environ.get("OPENAI_API_KEY"):
            return True, "OPENAI_API_KEY missing; returned prompt unchanged."
        return False, ""

    def _get_limiter(self, rate_limit_per_minute: int) -> _RateLimiter:
        if self._limiter is None or self._limiter.per_minute != rate_limit_per_minute:
            self._limiter = _RateLimiter(per_minute=rate_limit_per_minute)
        return self._limiter

    def _rewrite_prompt(
        self, client: OpenAI, prompt: str, instructions: str, model: str, max_output_tokens: int
    ) -> str:
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            instructions=instructions,
            max_output_tokens=max_output_tokens,
        )
        if not getattr(resp, "output_text", None):
            raise ValueError("OpenAI response did not include output_text")
        return resp.output_text.strip()

    def _safety_check_prompt(
        self, client: OpenAI, prompt: str, model: str, max_output_tokens: int
    ) -> Tuple[str, str]:
        safety_instructions = (
            "Classify the prompt for safety. Return JSON with keys 'status' (ok|flagged) "
            "and 'prompt' (a safe, intent-preserving prompt). Keep the JSON concise."
        )
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
            instructions=safety_instructions,
            max_output_tokens=max_output_tokens,
        )
        raw = getattr(resp, "output_text", "").strip()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:  # pragma: no cover - protective
            raise ValueError(f"Safety check response was not valid JSON: {raw}") from exc
        status = payload.get("status")
        if status not in {"ok", "flagged"}:
            raise ValueError("Safety check JSON must include status of 'ok' or 'flagged'")
        sanitized_prompt = payload.get("prompt")
        if not sanitized_prompt or not isinstance(sanitized_prompt, str):
            raise ValueError("Safety check JSON must include a string prompt")
        return sanitized_prompt, status

    def assist(
        self,
        prompt: str,
        mode: str = "rewrite",
        instructions: str = "Rewrite the user prompt for clarity while preserving intent and safety.",
        model: str = "gpt-4o-mini",
        max_output_tokens: int = 200,
        rate_limit_per_minute: int = 30,
        bypass_online: bool = False,
    ) -> Tuple[str, str]:
        self._validate_inputs(prompt, model, max_output_tokens, rate_limit_per_minute)
        bypass, message = self._should_bypass(bypass_online)
        if bypass:
            return prompt, message

        limiter = self._get_limiter(rate_limit_per_minute)
        limiter.check()

        client = self._client_factory()
        if mode == "rewrite":
            rewritten = self._rewrite_prompt(client, prompt, instructions, model, max_output_tokens)
            return rewritten, f"Rewritten with {model}"
        if mode == "safety_check":
            sanitized_prompt, status = self._safety_check_prompt(client, prompt, model, max_output_tokens)
            return sanitized_prompt, f"Safety status: {status} via {model}"
        raise ValueError(f"Unsupported mode: {mode}")


NODE_CLASS_MAPPINGS = {"PromptAssistNode": PromptAssistNode}
NODE_DISPLAY_NAME_MAPPINGS = {"PromptAssistNode": "Prompt Assist (OpenAI)"}
