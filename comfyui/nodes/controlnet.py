"""ControlNet-enabled ComfyUI node for the app pipeline."""
from __future__ import annotations

from typing import Dict, Tuple

from .config import load_pipeline_config
from .pipeline import BasePipelineNode


class ControlNetNode(BasePipelineNode):
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Dict]]:
        config = load_pipeline_config()
        return {
            "required": {
                "image": ("IMAGE", {}),
                "control_image": ("IMAGE", {}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
                "preset": ("STRING", {"default": "controlnet"}),
                "control_mode": ("STRING", {"default": "canny"}),
                "strength": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "scheduler": ("STRING", {"default": config.scheduler}),
            }
        }

    RETURN_TYPES = ("IMAGE", "DICT")
    FUNCTION = "render"
    CATEGORY = "App/Pipelines"

    def render(
        self,
        image,
        control_image,
        prompt: str,
        negative_prompt: str,
        seed: int,
        preset: str,
        control_mode: str,
        strength: float,
        scheduler: str,
    ) -> Tuple[list, Dict]:
        payload = {
            "model_key": "controlnet",
            "image": image,
            "control_image": control_image,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "preset": preset,
            "control_mode": control_mode,
            "strength": strength,
            "scheduler": scheduler,
        }
        response = self._forward("controlnet", payload)
        images = self._parse_images(response)
        metadata = {
            "seed": seed,
            "preset": preset,
            "control_mode": control_mode,
            "scheduler": scheduler,
        }
        return images, metadata


NODE_CLASS_MAPPINGS = {"AppControlNet": ControlNetNode}
NODE_DISPLAY_NAME_MAPPINGS = {"AppControlNet": "App: ControlNet"}

__all__ = ["ControlNetNode", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
