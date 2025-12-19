import sys
sys.path.append('../ai_pipeline')

import os
import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import (
    VideoJob, VideoStatus, ModelImage, Background,
    Action, VoiceTemplate, Product
)
from api.schemas import VideoGenerationRequest
from config.settings import settings
from services.worker import generate_video_task
from loguru import logger


async def create_video_job(
    request: VideoGenerationRequest,
    db: Session
) -> VideoJob:
    """
    Create a new video generation job
    """
    # Validate references exist
    model_image = db.query(ModelImage).filter(ModelImage.id == request.model_image_id).first()
    if not model_image:
        raise ValueError("Model image not found")

    background = db.query(Background).filter(Background.id == request.background_id).first()
    if not background:
        raise ValueError("Background not found")

    action = db.query(Action).filter(Action.id == request.action_id).first()
    if not action:
        raise ValueError("Action not found")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Create job record
    video_job = VideoJob(
        job_id=job_id,
        product_id=request.product_id,
        model_image_id=request.model_image_id,
        background_id=request.background_id,
        action_id=request.action_id,
        voice_template_id=request.voice_template_id,
        audio_text=request.audio_text,
        emotion=request.emotion,
        duration=request.duration,
        status=VideoStatus.PENDING,
        config={
            "model_image": model_image.file_path,
            "background": background.file_path,
            "action": action.name,
            "audio_text": request.audio_text,
            "emotion": request.emotion.value,
            "duration": request.duration,
            "custom_config": request.custom_config
        }
    )

    db.add(video_job)
    db.commit()
    db.refresh(video_job)

    logger.info(f"Video job created: {job_id}")

    # Queue the job for processing
    generate_video_task.delay(job_id)

    return video_job


async def get_job_status(job_id: str, db: Session) -> Optional[VideoJob]:
    """Get video job status"""
    return db.query(VideoJob).filter(VideoJob.job_id == job_id).first()


async def list_jobs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None
) -> List[VideoJob]:
    """List video jobs"""
    query = db.query(VideoJob)

    if status:
        query = query.filter(VideoJob.status == status)

    return query.order_by(VideoJob.created_at.desc()).offset(skip).limit(limit).all()


async def process_video_job(job_id: str):
    """
    Process video generation job
    This is called by Celery worker
    """
    from models.database import SessionLocal
    from ai_pipeline.video_generation.video_generator import VideoGenerator
    from ai_pipeline.voice_synthesis.bark_synthesizer import BarkSynthesizer

    db = SessionLocal()

    try:
        # Get job
        job = db.query(VideoJob).filter(VideoJob.job_id == job_id).first()
        if not job:
            logger.error(f"Job not found: {job_id}")
            return

        # Update status
        job.status = VideoStatus.PROCESSING
        job.started_at = datetime.utcnow()
        db.commit()

        logger.info(f"Processing video job: {job_id}")

        # Get references
        model_image = db.query(ModelImage).filter(ModelImage.id == job.model_image_id).first()
        background = db.query(Background).filter(Background.id == job.background_id).first()
        action = db.query(Action).filter(Action.id == job.action_id).first()

        # Prepare paths
        output_dir = os.path.join(settings.UPLOAD_DIR, "videos")
        os.makedirs(output_dir, exist_ok=True)

        audio_path = None

        # Generate audio if text provided
        if job.audio_text:
            logger.info("Generating audio...")
            job.progress = 0.2
            db.commit()

            audio_dir = os.path.join(settings.UPLOAD_DIR, "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, f"{job_id}.wav")

            synthesizer = BarkSynthesizer(model_size=settings.BARK_MODEL_SIZE)
            synthesizer.synthesize(
                text=job.audio_text,
                emotion=job.emotion.value,
                output_path=audio_path
            )

            logger.info(f"Audio generated: {audio_path}")

        # Generate video
        logger.info("Generating video...")
        job.progress = 0.5
        db.commit()

        video_path = os.path.join(output_dir, f"{job_id}.mp4")

        generator = VideoGenerator(
            use_local=settings.USE_LOCAL_MODELS,
            replicate_token=settings.REPLICATE_API_TOKEN
        )

        await generator.generate_video(
            model_image_path=model_image.file_path,
            background_path=background.file_path,
            action_data={
                "name": action.name,
                "pose_sequence": action.pose_sequence
            },
            audio_path=audio_path,
            output_path=video_path,
            duration=job.duration
        )

        # Update job
        job.status = VideoStatus.COMPLETED
        job.progress = 1.0
        job.output_video_path = video_path
        job.output_video_url = f"/uploads/videos/{job_id}.mp4"
        job.completed_at = datetime.utcnow()
        job.processing_time = (job.completed_at - job.started_at).total_seconds()

        db.commit()

        logger.info(f"Video job completed: {job_id}")

    except Exception as e:
        logger.error(f"Video generation failed: {e}")

        # Update job with error
        job.status = VideoStatus.FAILED
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()
