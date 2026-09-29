"""Storage Service supporting Supabase Storage and local fallback."""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from ..config import get_settings
from ..supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
settings = get_settings()


async def save_uploaded_image(file: UploadFile, prefix: str = "meal") -> str:
    """Save an uploaded meal image and return its accessible public URL or path."""
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    file_id = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"
    contents = await file.read()
    await file.seek(0)

    # 1. Attempt Supabase Storage
    try:
        supabase = get_supabase_client()
        bucket = settings.supabase_storage_bucket or "meals"
        supabase.storage.from_(bucket).upload(file_id, contents, {"content-type": file.content_type or "image/jpeg"})
        public_url = supabase.storage.from_(bucket).get_public_url(file_id)
        if public_url:
            return public_url
    except Exception as e:
        logger.debug("Supabase storage upload skipped or failed: %s. Using local disk.", e)

    # 2. Local disk fallback
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    with open(destination, "wb") as f:
        f.write(contents)

    backend_base = f"http://127.0.0.1:{settings.port}"
    return f"{backend_base}/uploads/{file_id}"


class StorageService:
    """Storage wrapper class."""

    async def save_image(self, file: UploadFile, prefix: str = "meal") -> str:
        return await save_uploaded_image(file, prefix)


_storage_service = StorageService()


def get_storage_service() -> StorageService:
    return _storage_service
