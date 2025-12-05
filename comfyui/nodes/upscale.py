"""Upscaling node wrapper for the app pipeline."""
from __future__ import annotations

from typing import Dict, Tuple

from .config import load_pipeline_config
from .pipeline import BasePipelineNode


class UpscaleNode(BasePipelineNode):
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Dict]]:
        config = load_pipeline_config()
        return {
            "required": {
                "image": ("IMAGE", {}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
                "preset": ("STRING", {"default": "refiner"}),
                "scale": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.1}),
                "scheduler": ("STRING", {"default": config.scheduler}),
            }
        }

    RETURN_TYPES = ("IMAGE", "DICT")
    FUNCTION = "render"
    CATEGORY = "App/Pipelines"

    def render(
        self,
        image,
        seed: int,
        preset: str,
        scale: float,
        scheduler: str,
    ) -> Tuple[list, Dict]:
        payload = {
            "model_key": "upscale",
            "image": image,
            "seed": seed,
            "preset": preset,
            "scale": scale,
            "scheduler": scheduler,
        }
        response = self._forward("upscale", payload)
        images = self._parse_images(response)
        metadata = {"seed": seed, "preset": preset, "scheduler": scheduler, "scale": scale}
        return images, metadata


NODE_CLASS_MAPPINGS = {"AppUpscale": UpscaleNode}
NODE_DISPLAY_NAME_MAPPINGS = {"AppUpscale": "App: Upscale"}

__all__ = ["UpscaleNode", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
