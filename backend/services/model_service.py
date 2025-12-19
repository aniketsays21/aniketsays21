import os
import uuid
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.database import ModelImage, Action
from config.settings import settings
from PIL import Image
import aiofiles
from loguru import logger


async def upload_model_image(file: UploadFile, name: str, db: Session) -> ModelImage:
    """
    Upload and process model image
    """
    # Validate file
    if not file.content_type.startswith("image/"):
        raise ValueError("File must be an image")

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"

    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, "models")
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, filename)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Create thumbnail
    thumbnail_path = await _create_thumbnail(file_path, upload_dir, file_id)

    # Generate URLs (adjust based on your storage setup)
    file_url = f"/uploads/models/{filename}"
    thumbnail_url = f"/uploads/models/thumbnails/{file_id}_thumb.jpg"

    # Save to database
    model_image = ModelImage(
        name=name,
        file_path=file_path,
        file_url=file_url,
        thumbnail_url=thumbnail_url,
        is_custom=True
    )

    db.add(model_image)
    db.commit()
    db.refresh(model_image)

    logger.info(f"Model image uploaded: {model_image.id}")
    return model_image


async def get_models(db: Session, skip: int = 0, limit: int = 100) -> List[ModelImage]:
    """Get list of model images"""
    return db.query(ModelImage).offset(skip).limit(limit).all()


async def get_actions(db: Session) -> List[Action]:
    """Get list of available actions"""
    return db.query(Action).filter(Action.is_active == True).all()


async def _create_thumbnail(image_path: str, upload_dir: str, file_id: str) -> str:
    """Create thumbnail for image"""
    try:
        img = Image.open(image_path)
        img.thumbnail((200, 200), Image.Resampling.LANCZOS)

        # Create thumbnail directory
        thumb_dir = os.path.join(upload_dir, "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)

        thumb_path = os.path.join(thumb_dir, f"{file_id}_thumb.jpg")
        img.save(thumb_path, "JPEG", quality=85)

        return thumb_path
    except Exception as e:
        logger.error(f"Failed to create thumbnail: {e}")
        return ""
