"""Custom ComfyUI nodes that forward to the app pipeline service."""
from .config import PipelineConfig, SettingsStore, load_pipeline_config
from .controlnet import ControlNetNode, NODE_CLASS_MAPPINGS as CONTROL_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as CONTROL_DISPLAY
from .img2img import Img2ImgNode, NODE_CLASS_MAPPINGS as IMG2IMG_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as IMG2IMG_DISPLAY
from .pipeline import BasePipelineNode, PipelineServiceClient
from .txt2img import Txt2ImgNode, NODE_CLASS_MAPPINGS as TXT2IMG_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TXT2IMG_DISPLAY
from .upscale import UpscaleNode, NODE_CLASS_MAPPINGS as UPSCALE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as UPSCALE_DISPLAY

NODE_CLASS_MAPPINGS = {
    **TXT2IMG_MAPPINGS,
    **IMG2IMG_MAPPINGS,
    **CONTROL_MAPPINGS,
    **UPSCALE_MAPPINGS,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    **TXT2IMG_DISPLAY,
    **IMG2IMG_DISPLAY,
    **CONTROL_DISPLAY,
    **UPSCALE_DISPLAY,
}

__all__ = [
    "BasePipelineNode",
    "PipelineServiceClient",
    "Txt2ImgNode",
    "Img2ImgNode",
    "ControlNetNode",
    "UpscaleNode",
    "PipelineConfig",
    "SettingsStore",
    "load_pipeline_config",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
