from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.upload import UploadResult

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
PRODUCT_UPLOAD_SUBDIR = "products"


async def save_product_image(file: UploadFile) -> UploadResult:
    original_name = file.filename or ""
    extension = Path(original_name).suffix.lower()
    content_type = file.content_type or "application/octet-stream"

    if extension not in ALLOWED_IMAGE_EXTENSIONS or content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg, png, webp and gif images are allowed",
        )

    content = await file.read()
    size = len(content)
    if size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    if size > settings.max_upload_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is larger than 5MB")

    upload_dir = settings.upload_dir / PRODUCT_UPLOAD_SUBDIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    target = upload_dir / filename
    target.write_bytes(content)

    return UploadResult(
        url=f"/uploads/{PRODUCT_UPLOAD_SUBDIR}/{filename}",
        filename=filename,
        size=size,
        content_type=content_type,
    )
