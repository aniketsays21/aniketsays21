import sys
from pathlib import Path

# Add project root to Python path for ai_pipeline imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from config.settings import settings
from models.database import get_db, init_db
from api import schemas
from services import (
    scraper_service,
    model_service,
    background_service,
    voice_service,
    video_service
)

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


# Model Management
@app.post("/api/upload-model", response_model=schemas.ModelImageResponse)
async def upload_model_image(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a custom model image"""
    try:
        model_image = await model_service.upload_model_image(file, name, db)
        return model_image
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/models", response_model=List[schemas.ModelImageResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of available model images"""
    models = await model_service.get_models(db, skip=skip, limit=limit)
    return models


# Backgrounds
@app.get("/api/backgrounds", response_model=List[schemas.BackgroundResponse])
async def list_backgrounds(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of available backgrounds"""
    backgrounds = await background_service.get_backgrounds(db, category=category)
    return backgrounds


@app.post("/api/backgrounds", response_model=schemas.BackgroundResponse)
async def upload_background(
    file: UploadFile = File(...),
    name: str = Form(...),
    category: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload a new background"""
    try:
        background = await background_service.upload_background(file, name, category, db)
        return background
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Actions
@app.get("/api/actions", response_model=List[schemas.ActionResponse])
async def list_actions(db: Session = Depends(get_db)):
    """Get list of available actions"""
    actions = await model_service.get_actions(db)
    return actions


# Voice
@app.post("/api/upload-voice", response_model=schemas.VoiceTemplateResponse)
async def upload_voice(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a custom voice sample for cloning"""
    try:
        voice = await voice_service.upload_voice(file, name, db)
        return voice
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/voices", response_model=List[schemas.VoiceTemplateResponse])
async def list_voices(db: Session = Depends(get_db)):
    """Get list of available voice templates"""
    voices = await voice_service.get_voices(db)
    return voices


# Video Generation
@app.post("/api/generate", response_model=schemas.VideoJobResponse)
async def generate_video(
    request: schemas.VideoGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a UGC video
    This is async - returns job_id to track progress
    """
    try:
        job = await video_service.create_video_job(request, db)
        return job
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/video/{job_id}", response_model=schemas.VideoJobResponse)
async def get_video_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get video generation status and result"""
    job = await video_service.get_job_status(job_id, db)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/videos", response_model=List[schemas.VideoJobResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all video jobs"""
    jobs = await video_service.list_jobs(db, skip=skip, limit=limit, status=status)
    return jobs


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
