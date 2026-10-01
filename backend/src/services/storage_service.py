"""Image storage service backed by Supabase Storage."""

import uuid
from fastapi import UploadFile

from ..config import get_settings
from ..supabase_client import get_supabase_storage_client

settings = get_settings()


async def save_uploaded_image(file: UploadFile, prefix: str = "meal") -> str:
    """Save an uploaded meal image and return its accessible public URL or path."""
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    file_id = f"{prefix}_{uuid.uuid4().hex[:12]}.{ext}"
    contents = await file.read()
    await file.seek(0)

    supabase = get_supabase_storage_client()
    bucket = settings.supabase_storage_bucket or "meals"
    supabase.storage.from_(bucket).upload(
        file_id,
        contents,
        {"content-type": file.content_type or "image/jpeg"},
    )
    public_url = supabase.storage.from_(bucket).get_public_url(file_id)
    if not public_url:
        raise RuntimeError("Supabase Storage did not return a public URL for the uploaded image.")
    return public_url


class StorageService:
    """Storage wrapper class."""

    async def save_image(self, file: UploadFile, prefix: str = "meal") -> str:
        return await save_uploaded_image(file, prefix)


_storage_service = StorageService()


def get_storage_service() -> StorageService:
    return _storage_service
