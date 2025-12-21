from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from config.settings import settings
from models.database import get_db, init_db
from api import schemas

# Only import scraper_service for now (other services need heavy dependencies)
from services import scraper_service

# Lazy import other services only when needed
model_service = None
background_service = None
voice_service = None
video_service = None

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

# Video Generation - disabled for local development
@app.post("/api/generate")
async def generate_video():
    raise HTTPException(status_code=503, detail="Video generation not available in local dev mode")

@app.get("/api/video/{job_id}")
async def get_video_status(job_id: str):
    raise HTTPException(status_code=503, detail="Video service not available in local dev mode")

@app.get("/api/videos")
async def list_videos():
    return []


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
