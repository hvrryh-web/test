"""Command line utility for ComfyUI smoke validation."""
from __future__ import annotations

import argparse
import sys

from agent.comfyui import (
    ComfyUIConfig,
    ComfyUIHealthCheck,
    ComfyUIRuntime,
    load_default_config,
)


def _build_runtime(config_path: str | None) -> ComfyUIRuntime:
    if config_path is None:
        config = load_default_config()
    else:
        config = ComfyUIConfig.from_file(config_path)
    runtime = ComfyUIRuntime(config)
    runtime.register_default_nodes()
    return runtime


def run_health_check(config_path: str | None = None) -> int:
    runtime = _build_runtime(config_path)
    health = ComfyUIHealthCheck(runtime.config, runtime.registry).run()
    if health.ok:
        print("ComfyUI health check passed:")
        for key, value in health.details.items():
            print(f"- {key}: {value}")
        return 0
    print("ComfyUI health check failed:")
    for err in health.errors:
        print(f"- {err}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ComfyUI helper CLI")
    parser.add_argument("command", choices=["health-check", "launch"], help="Action to perform")
    parser.add_argument(
        "--config",
        dest="config_path",
        default=None,
        help="Optional path to a comfyui config.yaml. Defaults to resources/comfyui/config.yaml",
    )
    args = parser.parse_args(argv)

    runtime = _build_runtime(args.config_path)
    if args.command == "health-check":
        return run_health_check(args.config_path)

    health = ComfyUIHealthCheck(runtime.config, runtime.registry).run()
    if not health.ok:
        print("ComfyUI launch aborted due to failing health check:")
        for err in health.errors:
            print(f"- {err}")
        return 1

    print(f"Launching ComfyUI with model {runtime.config.model.name} and scheduler {runtime.config.scheduler.name}...")
    print("(Launch is stubbed for smoke tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
