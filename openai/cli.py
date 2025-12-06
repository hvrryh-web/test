"""Placeholder CLI entrypoint for the stub openai package."""

import sys


def main() -> int:
    sys.stderr.write(
        "This repository ships a minimal openai stub. Install the official `openai` "
        "package from PyPI for full CLI functionality.\n"
    )
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
