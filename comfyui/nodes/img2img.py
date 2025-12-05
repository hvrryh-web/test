"""ComfyUI node that wraps the application's image-to-image pipeline."""
from __future__ import annotations

from typing import Dict, Tuple

from .config import load_pipeline_config
from .pipeline import BasePipelineNode


class Img2ImgNode(BasePipelineNode):
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Dict]]:
        config = load_pipeline_config()
        return {
            "required": {
                "image": ("IMAGE", {}),
                "prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2**32 - 1}),
                "preset": ("STRING", {"default": "image-to-image"}),
                "denoise": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.01}),
                "scheduler": ("STRING", {"default": config.scheduler}),
            }
        }

    RETURN_TYPES = ("IMAGE", "DICT")
    FUNCTION = "render"
    CATEGORY = "App/Pipelines"

    def render(
        self,
        image,
        prompt: str,
        negative_prompt: str,
        seed: int,
        preset: str,
        denoise: float,
        scheduler: str,
    ) -> Tuple[list, Dict]:
        payload = {
            "model_key": "img2img",
            "image": image,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "preset": preset,
            "denoise": denoise,
            "scheduler": scheduler,
        }
        response = self._forward("img2img", payload)
        images = self._parse_images(response)
        metadata = {"seed": seed, "preset": preset, "scheduler": scheduler}
        return images, metadata


NODE_CLASS_MAPPINGS = {"AppImg2Img": Img2ImgNode}
NODE_DISPLAY_NAME_MAPPINGS = {"AppImg2Img": "App: Img2Img"}

__all__ = ["Img2ImgNode", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
