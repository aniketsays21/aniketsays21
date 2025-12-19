import sys
sys.path.append('../ai_pipeline')

import os
import uuid
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.database import VoiceTemplate, EmotionType
from config.settings import settings
import aiofiles
from loguru import logger


async def upload_voice(file: UploadFile, name: str, db: Session) -> VoiceTemplate:
    """
    Upload voice sample for cloning
    """
    # Validate file
    allowed_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav"]
    if file.content_type not in allowed_types:
        raise ValueError(f"File must be audio (mp3 or wav)")

    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"

    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, "voices")
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, filename)
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Save to database
    voice_template = VoiceTemplate(
        name=name,
        file_path=file_path,
        emotion=EmotionType.NEUTRAL,
        is_custom=True
    )

    db.add(voice_template)
    db.commit()
    db.refresh(voice_template)

    logger.info(f"Voice template uploaded: {voice_template.id}")
    return voice_template


async def get_voices(db: Session) -> List[VoiceTemplate]:
    """Get list of voice templates"""
    return db.query(VoiceTemplate).all()


async def synthesize_voice(
    text: str,
    emotion: EmotionType,
    output_path: str
) -> str:
    """
    Synthesize voice using Bark

    Args:
        text: Text to synthesize
        emotion: Emotion type
        output_path: Where to save the audio

    Returns:
        Path to generated audio file
    """
    from ai_pipeline.voice_synthesis.bark_synthesizer import BarkSynthesizer

    try:
        synthesizer = BarkSynthesizer(model_size=settings.BARK_MODEL_SIZE)
        result = synthesizer.synthesize(
            text=text,
            emotion=emotion.value,
            output_path=output_path
        )
        return result
    except Exception as e:
        logger.error(f"Voice synthesis failed: {e}")
        raise
