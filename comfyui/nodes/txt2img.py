"""ComfyUI node that wraps the application's text-to-image pipeline."""
from __future__ import annotations

from typing import Dict, Tuple

from .config import load_pipeline_config
from .pipeline import BasePipelineNode


class Txt2ImgNode(BasePipelineNode):
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Dict]]:
        config = load_pipeline_config()
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
                "preset": ("STRING", {"default": "standard"}),
                "steps": ("INT", {"default": 28, "min": 1, "max": 200}),
                "cfg_scale": ("FLOAT", {"default": 7.5, "min": 0.0, "max": 30.0}),
                "width": ("INT", {"default": 768, "min": 64, "max": 2048, "step": 64}),
                "height": ("INT", {"default": 768, "min": 64, "max": 2048, "step": 64}),
                "scheduler": ("STRING", {"default": config.scheduler}),
            }
        }

    RETURN_TYPES = ("IMAGE", "DICT")
    FUNCTION = "render"
    CATEGORY = "App/Pipelines"

    def render(
        self,
        prompt: str,
        negative_prompt: str,
        seed: int,
        preset: str,
        steps: int,
        cfg_scale: float,
        width: int,
        height: int,
        scheduler: str,
    ) -> Tuple[list, Dict]:
        payload = {
            "model_key": "txt2img",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "preset": preset,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "scheduler": scheduler,
        }
        response = self._forward("txt2img", payload)
        images = self._parse_images(response)
        metadata = {"seed": seed, "preset": preset, "scheduler": scheduler}
        return images, metadata


NODE_CLASS_MAPPINGS = {"AppTxt2Img": Txt2ImgNode}
NODE_DISPLAY_NAME_MAPPINGS = {"AppTxt2Img": "App: Txt2Img"}

__all__ = ["Txt2ImgNode", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
