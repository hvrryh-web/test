from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from agent.comfyui import (
    ComfyUIConfig,
    ComfyUIHealthCheck,
    ComfyUIRuntime,
    smoke_suite_enabled,
)

CONFIG_PATH = PROJECT_ROOT / "resources" / "comfyui" / "config.yaml"


@pytest.fixture(scope="session")
def comfy_runtime() -> ComfyUIRuntime:
    config = ComfyUIConfig.from_file(CONFIG_PATH)
    runtime = ComfyUIRuntime(config)
    runtime.register_default_nodes()
    return runtime


@pytest.mark.comfyui_smoke
@pytest.mark.slow
@pytest.mark.skipif(not smoke_suite_enabled(), reason="ComfyUI smoke suite requires GPU or explicit opt-in")
def test_txt2img_metadata_consistency(comfy_runtime: ComfyUIRuntime) -> None:
    health = ComfyUIHealthCheck(comfy_runtime.config, comfy_runtime.registry).run()
    assert health.ok, f"health check failed: {health.errors}"

    prompt = "a cozy cabin in the snow"
    result_a = comfy_runtime.generate_txt2img(prompt=prompt, seed=7)
    result_b = comfy_runtime.generate_txt2img(prompt=prompt, seed=7)

    assert result_a.image == result_b.image
    assert result_a.metadata["seed"] == 7
    assert result_a.metadata["model"]["name"] == comfy_runtime.config.model.name
    assert result_a.metadata["scheduler"]["steps"] == comfy_runtime.config.scheduler.steps
    assert result_a.metadata["image_hash"] == result_b.metadata["image_hash"]
    assert result_a.metadata["node"] == "txt2img"
    assert result_a.metadata["prompt"] == prompt


@pytest.mark.comfyui_smoke
@pytest.mark.slow
@pytest.mark.skipif(not smoke_suite_enabled(), reason="ComfyUI smoke suite requires GPU or explicit opt-in")
def test_img2img_metadata_consistency(comfy_runtime: ComfyUIRuntime) -> None:
    base = comfy_runtime.generate_txt2img(prompt="source", seed=11)
    derived = comfy_runtime.generate_img2img(base.image, seed=11)

    assert derived.metadata["seed"] == 11
    assert derived.metadata["node"] == "img2img"
    assert derived.metadata["source_hash"] == base.metadata["image_hash"]
    assert derived.metadata["model"]["path"].endswith("base.safetensors")
    assert derived.metadata["scheduler"]["name"] == comfy_runtime.config.scheduler.name
    assert derived.image != base.image
    assert derived.metadata["image_hash"] != base.metadata["image_hash"]


@pytest.mark.comfyui_smoke
@pytest.mark.slow
@pytest.mark.skipif(not smoke_suite_enabled(), reason="ComfyUI smoke suite requires GPU or explicit opt-in")
def test_health_check_reports_registered_nodes(comfy_runtime: ComfyUIRuntime) -> None:
    health = ComfyUIHealthCheck(comfy_runtime.config, comfy_runtime.registry).run()
    assert health.ok
    assert set(health.details.get("nodes", [])) >= {"txt2img", "img2img"}
    assert "scheduler" in health.details
