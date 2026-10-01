"""HTTP service that exposes the Docta YOLO model at ``POST /detect``."""

from __future__ import annotations

import base64
import binascii
import io
import os
import threading
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException, Request
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

try:
    from .model import DEFAULT_WEIGHTS_PATH, DoctaObjectDetector
except ImportError:
    from model import DEFAULT_WEIGHTS_PATH, DoctaObjectDetector


MAX_IMAGE_BYTES = 20 * 1024 * 1024
CONFIDENCE_THRESHOLD = float(os.getenv("DOCTA_CV_CONFIDENCE", "0.25"))
if not 0.0 <= CONFIDENCE_THRESHOLD <= 1.0:
    raise ValueError("DOCTA_CV_CONFIDENCE must be between 0 and 1.")
_detector: Optional[DoctaObjectDetector] = None
_inference_lock = threading.Lock()
app = FastAPI(title="Docta Food Detection Service", version="1.0.0")


def _has_supported_signature(data: bytes) -> bool:
    return (
        data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"\x89PNG\r\n\x1a\n")
        or data.startswith((b"GIF87a", b"GIF89a"))
        or data.startswith(b"BM")
        or (data.startswith(b"RIFF") and data[8:12] == b"WEBP")
        or data.startswith((b"II*\x00", b"MM\x00*"))
    )


def _get_detector() -> DoctaObjectDetector:
    global _detector
    if _detector is None:
        weights_path = os.getenv("DOCTA_MODEL_WEIGHTS", str(DEFAULT_WEIGHTS_PATH))
        device = os.getenv("DOCTA_CV_DEVICE") or None
        _detector = DoctaObjectDetector(weights_path=weights_path, device=device)
    return _detector


def _decode_image(data: bytes) -> Image.Image:
    if not data:
        raise HTTPException(status_code=400, detail="Image data is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 20 MB limit.")
    if not _has_supported_signature(data):
        raise HTTPException(status_code=415, detail="Uploaded data is not a supported image.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            return image.convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=415, detail="Uploaded data is not a supported image.") from exc


def _allowed_image_hosts() -> set[str]:
    values = os.getenv("DOCTA_ALLOWED_IMAGE_HOSTS", "").split(",")
    hosts = {value.strip().lower() for value in values if value.strip()}
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_host = urlparse(supabase_url).hostname
    if supabase_host:
        hosts.add(supabase_host.lower())
    return hosts


async def _load_image_url(image_url: str) -> Image.Image:
    parsed = urlparse(image_url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise HTTPException(status_code=400, detail="Image URLs must use HTTPS.")
    if parsed.hostname.lower() not in _allowed_image_hosts():
        raise HTTPException(
            status_code=400,
            detail="Image URL host is not allowed. Configure DOCTA_ALLOWED_IMAGE_HOSTS.",
        )

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
            async with client.stream("GET", image_url) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if not content_type.startswith("image/"):
                    raise HTTPException(status_code=415, detail="Image URL did not return an image.")
                chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > MAX_IMAGE_BYTES:
                        raise HTTPException(status_code=413, detail="Image exceeds the 20 MB limit.")
                return _decode_image(bytes(chunks))
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=400, detail=f"Could not retrieve image URL: {exc}") from exc


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ready", "model_loaded": _detector is not None}


@app.post("/detect")
async def detect(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "").lower()
    prompt: Optional[str] = None

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        file = form.get("file") or form.get("image")
        prompt_value = form.get("prompt")
        prompt = str(prompt_value) if prompt_value is not None else None
        if file is None or not hasattr(file, "read"):
            raise HTTPException(status_code=400, detail="Multipart request must include an image file.")
        data = await file.read(MAX_IMAGE_BYTES + 1)
        image = _decode_image(data)
    elif "application/json" in content_type:
        payload = await request.json()
        prompt = payload.get("prompt")
        image_url = payload.get("image_url")
        image_base64 = payload.get("image_base64")
        if image_base64:
            encoded = image_base64.split(",", 1)[-1]
            try:
                image = _decode_image(base64.b64decode(encoded, validate=True))
            except (binascii.Error, ValueError) as exc:
                raise HTTPException(status_code=400, detail="image_base64 is invalid.") from exc
        elif image_url:
            image = await _load_image_url(str(image_url))
        else:
            raise HTTPException(status_code=400, detail="Provide image_url or image_base64.")
    else:
        raise HTTPException(status_code=415, detail="Use multipart/form-data or application/json.")

    del prompt  # Accepted for API compatibility; this detector is image-only.
    detector = _get_detector()
    def _infer() -> dict[str, Any]:
        with _inference_lock:
            return detector.detect(image, CONFIDENCE_THRESHOLD)

    return await run_in_threadpool(_infer)
