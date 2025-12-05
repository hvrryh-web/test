"""Lightweight ComfyUI-inspired runtime helpers and health checks.

This module does not aim to replicate ComfyUI. Instead, it provides
minimal hooks to validate configuration and deterministic pseudo-image
outputs so smoke tests can reason about metadata and registry state.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Sequence

import ruamel.yaml as yaml


@dataclass
class ModelDefinition:
    """Represents a model checkpoint that should be available to the runtime."""

    name: str
    path: Path
    format: str = "safetensors"

    def available(self) -> bool:
        return self.path.exists()


@dataclass
class SchedulerDefinition:
    """Represents a diffusion scheduler configuration."""

    name: str
    steps: int
    beta_start: float
    beta_end: float

    def validate(self) -> None:
        if self.steps <= 0:
            raise ValueError("steps must be positive")
        if not (0 <= self.beta_start < self.beta_end <= 1):
            raise ValueError("beta range must be between 0 and 1 and start < end")


class NodeRegistry:
    """Registry for simple callable nodes used by the smoke runtime."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Callable[..., GenerationResult]] = {}

    def register(self, name: str, handler: Callable[..., "GenerationResult"]) -> None:
        self._nodes[name] = handler

    def ensure_registered(self, required: Iterable[str]) -> None:
        missing = [node for node in required if node not in self._nodes]
        if missing:
            raise ValueError(f"Missing node registrations: {', '.join(sorted(missing))}")

    def names(self) -> List[str]:
        return sorted(self._nodes)

    def get(self, name: str) -> Callable[..., "GenerationResult"]:
        if name not in self._nodes:
            raise KeyError(f"Node '{name}' is not registered")
        return self._nodes[name]


@dataclass
class ComfyUIConfig:
    model: ModelDefinition
    scheduler: SchedulerDefinition
    required_nodes: Sequence[str]

    @classmethod
    def from_file(cls, path: os.PathLike[str] | str) -> "ComfyUIConfig":
        config_path = Path(path).resolve()
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.YAML().load(f)
        base_dir = config_path.parent
        model_raw = data.get("models", {})[data.get("default_model", "base")]
        scheduler_raw = data.get("schedulers", {})[data.get("default_scheduler", "euler")]
        required_nodes = data.get("required_nodes", ["txt2img", "img2img"])
        model = ModelDefinition(
            name=model_raw.get("name", "base"),
            path=(base_dir / model_raw["path"]).resolve(),
            format=model_raw.get("format", "safetensors"),
        )
        scheduler = SchedulerDefinition(
            name=data.get("default_scheduler", "euler"),
            steps=int(scheduler_raw.get("steps", 20)),
            beta_start=float(scheduler_raw.get("beta_start", 0.0001)),
            beta_end=float(scheduler_raw.get("beta_end", 0.02)),
        )
        return cls(model=model, scheduler=scheduler, required_nodes=required_nodes)


@dataclass
class GenerationResult:
    image: List[List[int]]
    metadata: Dict[str, Any]


class ComfyUIRuntime:
    """Small deterministic runtime used for smoke testing."""

    def __init__(self, config: ComfyUIConfig, registry: NodeRegistry | None = None) -> None:
        self.config = config
        self.registry = registry or NodeRegistry()

    def register_default_nodes(self) -> None:
        self.registry.register("txt2img", self.generate_txt2img)
        self.registry.register("img2img", self.generate_img2img)

    def _render_grid(self, seed: int, modifier: int = 0) -> List[List[int]]:
        rng = random.Random(seed + modifier)
        return [[rng.randint(0, 255) for _ in range(8)] for _ in range(8)]

    def _hash_image(self, image: List[List[int]]) -> str:
        blob = json.dumps(image, separators=(",", ":"), sort_keys=True)
        return hashlib.sha1(blob.encode("utf-8")).hexdigest()

    def _metadata(self, *, seed: int, node: str, prompt: str | None = None, source_hash: str | None = None) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "seed": seed,
            "node": node,
            "model": {
                "name": self.config.model.name,
                "path": str(self.config.model.path),
                "format": self.config.model.format,
            },
            "scheduler": {
                "name": self.config.scheduler.name,
                "steps": self.config.scheduler.steps,
                "beta_start": self.config.scheduler.beta_start,
                "beta_end": self.config.scheduler.beta_end,
            },
        }
        if prompt:
            metadata["prompt"] = prompt
        if source_hash:
            metadata["source_hash"] = source_hash
        return metadata

    def generate_txt2img(self, prompt: str, seed: int = 1) -> GenerationResult:
        image = self._render_grid(seed)
        metadata = self._metadata(seed=seed, node="txt2img", prompt=prompt)
        metadata["image_hash"] = self._hash_image(image)
        return GenerationResult(image=image, metadata=metadata)

    def generate_img2img(self, source_image: List[List[int]], seed: int = 1) -> GenerationResult:
        source_hash = self._hash_image(source_image)
        # nudge the seed with the hash to keep deterministic but distinct
        modifier = int(source_hash[:8], 16) % 97
        image = self._render_grid(seed, modifier=modifier)
        metadata = self._metadata(seed=seed, node="img2img", source_hash=source_hash)
        metadata["image_hash"] = self._hash_image(image)
        return GenerationResult(image=image, metadata=metadata)


@dataclass
class HealthCheckResult:
    ok: bool
    errors: List[str]
    details: Dict[str, Any]


class ComfyUIHealthCheck:
    def __init__(self, config: ComfyUIConfig, registry: NodeRegistry) -> None:
        self.config = config
        self.registry = registry

    def run(self) -> HealthCheckResult:
        errors: List[str] = []
        details: Dict[str, Any] = {}
        if not self.config.model.available():
            errors.append(f"Model checkpoint missing at {self.config.model.path}")
        try:
            self.config.scheduler.validate()
            details["scheduler"] = "valid"
        except ValueError as exc:
            errors.append(f"Scheduler configuration invalid: {exc}")
        try:
            self.registry.ensure_registered(self.config.required_nodes)
            details["nodes"] = self.registry.names()
        except ValueError as exc:
            errors.append(str(exc))
        return HealthCheckResult(ok=not errors, errors=errors, details=details)


def hardware_acceleration_available() -> bool:
    """Best-effort check to see if a GPU is advertised.

    We let callers override detection with ``COMFYUI_ASSUME_GPU`` to make the
    smoke suite runnable on CPU-only CI workers.
    """

    override = os.environ.get("COMFYUI_ASSUME_GPU")
    if override is not None:
        return override.lower() in {"1", "true", "yes"}
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def smoke_suite_enabled() -> bool:
    """Return True if the comfyUI smoke tests should execute."""

    if os.environ.get("COMFYUI_RUN_SMOKE_ON_CPU"):
        return True
    return hardware_acceleration_available()


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "resources" / "comfyui" / "config.yaml"


def load_default_config() -> ComfyUIConfig:
    return ComfyUIConfig.from_file(DEFAULT_CONFIG_PATH)
