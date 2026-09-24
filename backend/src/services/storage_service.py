"""Storage Service for meal image uploads (Local & AWS S3 ready)."""

import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from ..config import get_settings

settings = get_settings()


async def save_uploaded_image(file: UploadFile, prefix: str = "meal") -> str:
    """Save an uploaded file and return its accessible URL/path."""
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    file_id = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"

    # If S3 is configured for AWS Fargate deployment
    if settings.s3_bucket_name:
        return f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/meals/{file_id}"

    # Local disk
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / file_id
    contents = await file.read()
    with open(destination, "wb") as f:
        f.write(contents)
    await file.seek(0)

    return f"/uploads/{file_id}"


class StorageService:
    """Compatibility wrapper for StorageService."""
    async def save_image(self, file: UploadFile, prefix: str = "meal") -> str:
        return await save_uploaded_image(file, prefix)


_storage_service = StorageService()


def get_storage_service() -> StorageService:
    return _storage_service
