import os
import uuid
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.database import Background
from config.settings import settings
from PIL import Image
import aiofiles
from loguru import logger


async def upload_background(
    file: UploadFile,
    name: str,
    category: Optional[str],
    db: Session
) -> Background:
    """Upload a new background"""
    # Validate file
    if not file.content_type.startswith("image/"):
        raise ValueError("File must be an image")

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"

    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, "backgrounds")
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, filename)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Create thumbnail
    thumbnail_path = await _create_thumbnail(file_path, upload_dir, file_id)

    # Generate URLs
    file_url = f"/uploads/backgrounds/{filename}"
    thumbnail_url = f"/uploads/backgrounds/thumbnails/{file_id}_thumb.jpg"

    # Save to database
    background = Background(
        name=name,
        file_path=file_path,
        file_url=file_url,
        thumbnail_url=thumbnail_url,
        category=category,
        is_active=True
    )

    db.add(background)
    db.commit()
    db.refresh(background)

    logger.info(f"Background uploaded: {background.id}")
    return background


async def get_backgrounds(
    db: Session,
    category: Optional[str] = None
) -> List[Background]:
    """Get list of backgrounds"""
    query = db.query(Background).filter(Background.is_active == True)

    if category:
        query = query.filter(Background.category == category)

    return query.all()


async def _create_thumbnail(image_path: str, upload_dir: str, file_id: str) -> str:
    """Create thumbnail for background"""
    try:
        img = Image.open(image_path)
        img.thumbnail((300, 200), Image.Resampling.LANCZOS)

        thumb_dir = os.path.join(upload_dir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        thumb_path = os.path.join(thumb_dir, f"{file_id}_thumb.jpg")
        img.save(thumb_path, "JPEG", quality=85)

        return thumb_path
    except Exception as e:
        logger.error(f"Failed to create thumbnail: {e}")
        return ""
