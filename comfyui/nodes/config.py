"""Configuration loading for ComfyUI nodes.

The settings store is shared with the rest of the application so ComfyUI
nodes follow the same model paths, precision, and scheduler defaults.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict

DEFAULT_CONFIG_CANDIDATES = [
    os.getenv("APP_SETTINGS_PATH"),
    os.path.join(os.getcwd(), "agent", "agent_config.json"),
    os.path.join(os.path.dirname(__file__), "..", "..", "agent", "agent_config.json"),
]


@dataclass
class PipelineConfig:
    model_paths: Dict[str, str]
    precision: str
    scheduler: str
    api_host: str
    api_port: int
    api_token: str | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self.api_host}:{self.api_port}"


class SettingsStore:
    """Load the application settings that also drive the ComfyUI nodes."""

    def __init__(self, path: str | None = None):
        self.path = path or self._discover_path()

    def _discover_path(self) -> str:
        for candidate in DEFAULT_CONFIG_CANDIDATES:
            if candidate and os.path.exists(candidate):
                return os.path.abspath(candidate)
        raise FileNotFoundError("Unable to locate an app settings file for ComfyUI nodes")

    def read(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)


def _normalize_settings(raw: Dict[str, Any]) -> PipelineConfig:
    models = raw.get("models", {})
    precision = raw.get("precision") or raw.get("default_precision") or "fp16"
    scheduler = raw.get("scheduler") or raw.get("default_scheduler") or "euler_a"
    api_host = raw.get("api_host", "127.0.0.1")
    api_port = int(raw.get("api_port", 8080))
    return PipelineConfig(
        model_paths=models,
        precision=precision,
        scheduler=scheduler,
        api_host=api_host,
        api_port=api_port,
        api_token=raw.get("api_token"),
    )


@lru_cache(maxsize=1)
def load_pipeline_config(path: str | None = None) -> PipelineConfig:
    store = SettingsStore(path)
    raw_settings = store.read()
    return _normalize_settings(raw_settings)


__all__ = ["PipelineConfig", "SettingsStore", "load_pipeline_config"]
