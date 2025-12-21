from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uvicorn
import uuid
import os
import asyncio
import aiohttp
from datetime import datetime

from config.settings import settings
from models.database import get_db, init_db
from api import schemas

# Only import scraper_service for now (other services need heavy dependencies)
from services import scraper_service

# In-memory job storage (replace with Redis in production)
video_jobs: Dict[str, Dict[str, Any]] = {}

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Events
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    init_db()
    print(f"🚀 {settings.APP_NAME} started in {settings.APP_ENV} mode")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down...")


# Health check
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Product Scraping
@app.post("/api/scrape", response_model=schemas.ProductResponse)
async def scrape_product(
    request: schemas.ScrapeRequest,
    db: Session = Depends(get_db)
):
    """
    Scrape product information from URL
    Returns product title, description, images, and metadata
    """
    try:
        product = await scraper_service.scrape_product(request.url, db)
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Model Management - disabled for local development
@app.post("/api/upload-model")
async def upload_model_image(file: UploadFile = File(...), name: str = Form(...)):
    raise HTTPException(status_code=503, detail="Model upload not available in local dev mode")

@app.get("/api/models")
async def list_models():
    return []

# Backgrounds - disabled for local development
@app.get("/api/backgrounds")
async def list_backgrounds():
    return []

@app.post("/api/backgrounds")
async def upload_background(file: UploadFile = File(...), name: str = Form(...)):
    raise HTTPException(status_code=503, detail="Background upload not available in local dev mode")

# Actions - disabled for local development
@app.get("/api/actions")
async def list_actions():
    return []

# Voice - disabled for local development
@app.post("/api/upload-voice")
async def upload_voice(file: UploadFile = File(...), name: str = Form(...)):
    raise HTTPException(status_code=503, detail="Voice upload not available in local dev mode")

@app.get("/api/voices")
async def list_voices():
    return []

# Video Generation
async def download_image(url: str, save_path: str) -> str:
    """Download image from URL to local path"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(await response.read())
                return save_path
    raise Exception(f"Failed to download image from {url}")


async def run_video_generation(job_id: str, config: dict):
    """Background task to generate video"""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

    try:
        video_jobs[job_id]["status"] = "processing"
        video_jobs[job_id]["progress"] = 0.1
        video_jobs[job_id]["started_at"] = datetime.utcnow().isoformat()

        # Download model and background images
        temp_dir = os.path.join(settings.UPLOAD_DIR, "temp", job_id)
        os.makedirs(temp_dir, exist_ok=True)

        video_jobs[job_id]["progress"] = 0.2

        # Download model image
        model_path = os.path.join(temp_dir, "model.jpg")
        await download_image(config["model_image_url"], model_path)

        # Download background image
        bg_path = os.path.join(temp_dir, "background.jpg")
        await download_image(config["background_url"], bg_path)

        video_jobs[job_id]["progress"] = 0.4

        # Import video generator
        from ai_pipeline.video_generation import (
            get_video_generator,
            VideoModelType,
            VideoGenerationConfig
        )

        # Determine which model to use
        model_type_str = settings.VIDEO_MODEL.lower()
        if model_type_str == "wan2.1":
            model_type = VideoModelType.WAN21
        elif model_type_str == "svd":
            model_type = VideoModelType.SVD
        else:
            model_type = VideoModelType.PLACEHOLDER

        # Get generator
        generator = get_video_generator(model_type)
        await generator.load_model()

        video_jobs[job_id]["progress"] = 0.5

        # Prepare output path
        output_dir = os.path.join(settings.UPLOAD_DIR, "videos")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{job_id}.mp4")

        # Parse resolution
        res_parts = settings.VIDEO_RESOLUTION.split("x")
        resolution = (int(res_parts[0]), int(res_parts[1]))

        # Create config
        gen_config = VideoGenerationConfig(
            model_image_path=model_path,
            background_path=bg_path,
            action_type=config.get("action_type", "talking"),
            action_data=config.get("action_data", {}),
            output_path=output_path,
            duration=config.get("duration", 5.0),
            fps=settings.VIDEO_FPS,
            resolution=resolution
        )

        video_jobs[job_id]["progress"] = 0.6

        # Generate video
        result = await generator.generate(gen_config)

        video_jobs[job_id]["progress"] = 0.9

        if result.success:
            video_jobs[job_id]["status"] = "completed"
            video_jobs[job_id]["progress"] = 1.0
            video_jobs[job_id]["output_url"] = f"/api/video/{job_id}/download"
            video_jobs[job_id]["output_path"] = result.output_path
            video_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
            video_jobs[job_id]["model_used"] = result.model_used
            video_jobs[job_id]["generation_time"] = result.generation_time
        else:
            video_jobs[job_id]["status"] = "failed"
            video_jobs[job_id]["error_message"] = result.error_message

        # Cleanup temp files
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    except Exception as e:
        video_jobs[job_id]["status"] = "failed"
        video_jobs[job_id]["error_message"] = str(e)
        print(f"Video generation error: {e}")


@app.post("/api/generate")
async def generate_video(
    request: schemas.VideoGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Start video generation job.
    Returns job_id to poll for status.
    """
    job_id = str(uuid.uuid4())

    # Create job record
    video_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0.0,
        "created_at": datetime.utcnow().isoformat(),
        "config": {
            "model_image_url": request.model_image_url,
            "background_url": request.background_url,
            "action_type": request.action_type,
            "action_data": request.action_data or {},
            "duration": request.duration or 5.0,
            "audio_text": request.audio_text
        }
    }

    # Start background task
    background_tasks.add_task(
        run_video_generation,
        job_id,
        video_jobs[job_id]["config"]
    )

    return {"job_id": job_id, "status": "pending"}


@app.get("/api/video/{job_id}")
async def get_video_status(job_id: str):
    """Get video generation job status"""
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = video_jobs[job_id]
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job.get("progress", 0),
        "output_url": job.get("output_url"),
        "error_message": job.get("error_message"),
        "model_used": job.get("model_used"),
        "generation_time": job.get("generation_time"),
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at")
    }


@app.get("/api/video/{job_id}/download")
async def download_video(job_id: str):
    """Download generated video"""
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = video_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video not ready")

    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"ugc_video_{job_id}.mp4"
    )


@app.get("/api/videos")
async def list_videos():
    """List all video jobs"""
    return [
        {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job.get("progress", 0),
            "created_at": job.get("created_at"),
            "completed_at": job.get("completed_at")
        }
        for job in video_jobs.values()
    ]


@app.get("/api/video-models")
async def list_video_models():
    """List available video generation models"""
    return {
        "current_model": settings.VIDEO_MODEL,
        "available_models": [
            {
                "id": "placeholder",
                "name": "Placeholder (Testing)",
                "description": "Simple composite animation for testing the pipeline",
                "free": True,
                "gpu_required": False
            },
            {
                "id": "wan2.1",
                "name": "Wan 2.1",
                "description": "Alibaba's free image-to-video model",
                "free": True,
                "gpu_required": True,
                "vram_required": "12GB+"
            },
            {
                "id": "svd",
                "name": "Stable Video Diffusion",
                "description": "High-quality video generation via Replicate API",
                "free": False,
                "gpu_required": False,
                "cost": "~$0.05/video"
            }
        ]
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
