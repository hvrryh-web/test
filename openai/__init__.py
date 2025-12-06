"""Lightweight stub of the OpenAI client library.

This repository does not currently ship the full official client; this
module exists to satisfy imports in tooling and tests. For real API
functionality, install the published `openai` package from PyPI.
"""

from __future__ import annotations

__all__ = ["ChatCompletion", "__version__"]
__version__ = "2.8.1"


class _Unimplemented:
    @classmethod
    def create(cls, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise NotImplementedError(
            "The bundled stub does not implement API calls. Install the official "
            "`openai` package to perform real requests."
        )


class ChatCompletion(_Unimplemented):
    pass
