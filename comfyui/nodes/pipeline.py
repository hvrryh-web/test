"""Helpers for calling the app pipeline service from ComfyUI nodes."""
from __future__ import annotations

import base64
import io
from typing import Any, Dict, List

import httpx
import numpy as np
from PIL import Image

from .config import PipelineConfig, load_pipeline_config


class PipelineServiceClient:
    """Thin wrapper around the app's pipeline HTTP API."""

    def __init__(self, config: PipelineConfig | None = None, timeout: float = 60.0):
        self.config = config or load_pipeline_config()
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        return headers

    def invoke(self, route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.config.base_url}/pipeline/{route.strip('/')}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()


class BasePipelineNode:
    """Shared helpers for nodes that forward to the pipeline service."""

    def __init__(self) -> None:
        self.config = load_pipeline_config()
        self.client = PipelineServiceClient(self.config)

    def _inject_defaults(self, payload: Dict[str, Any], model_key: str) -> Dict[str, Any]:
        payload.setdefault("model", self.config.model_paths.get(model_key))
        payload.setdefault("precision", self.config.precision)
        payload.setdefault("scheduler", self.config.scheduler)
        return payload

    def _parse_images(self, response: Dict[str, Any]) -> List[np.ndarray]:
        images: List[np.ndarray] = []
        raw_images = response.get("images") or []
        for item in raw_images:
            data = base64.b64decode(item)
            with Image.open(io.BytesIO(data)) as img:
                # ComfyUI expects float32 arrays in 0-1 range
                images.append(np.array(img).astype(np.float32) / 255.0)
        return images

    def _forward(self, route: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        enriched = self._inject_defaults(payload, payload.get("model_key", "txt2img"))
        enriched.pop("model_key", None)
        return self.client.invoke(route, enriched)


__all__ = ["BasePipelineNode", "PipelineServiceClient"]
