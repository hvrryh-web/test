from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import Body, FastAPI, HTTPException

COMFYUI_API_URL = os.environ.get("COMFYUI_API_URL", "http://localhost:8188")

app = FastAPI(title="ComfyUI Facade", version="0.1.0")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "upstream": COMFYUI_API_URL}


@app.post("/prompt")
async def queue_prompt(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Forward a prompt payload to the upstream ComfyUI instance."""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{COMFYUI_API_URL}/prompt", json=payload, timeout=30)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - thin facade
            raise HTTPException(status_code=502, detail=str(exc))
    return response.json()
