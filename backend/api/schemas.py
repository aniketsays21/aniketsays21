from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class EmotionType(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SURPRISED = "surprised"


class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Schemas
class ScrapeRequest(BaseModel):
    url: str = Field(..., description="Product URL to scrape")


class VideoGenerationRequest(BaseModel):
    product_id: Optional[int] = Field(None, description="ID of scraped product")
    model_image_id: int = Field(..., description="ID of model image to use")
    background_id: int = Field(..., description="ID of background to use")
    action_id: int = Field(..., description="ID of action/pose to use")
    voice_template_id: Optional[int] = Field(None, description="ID of voice template")
    audio_text: Optional[str] = Field(None, description="Text to synthesize")
    audio_file_url: Optional[str] = Field(None, description="URL of uploaded audio")
    emotion: EmotionType = Field(EmotionType.NEUTRAL, description="Voice emotion")
    duration: float = Field(5.0, description="Video duration in seconds", ge=1, le=30)
    custom_config: Optional[Dict[str, Any]] = Field(None, description="Additional config")


class VideoGenerateRequest(BaseModel):
    """Simplified request for video generation with preset images"""
    model_image_url: str = Field(..., description="URL of model image")
    background_url: str = Field(..., description="URL of background image")
    action_type: str = Field("talking", description="Type of action/animation")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Action configuration")
    audio_text: Optional[str] = Field(None, description="Text for voice synthesis")
    duration: Optional[float] = Field(5.0, description="Video duration in seconds", ge=1, le=30)


# Response Schemas
class ProductResponse(BaseModel):
    id: int
    url: str
    title: str
    description: str
    price: Optional[str]
    images: List[str]
    scraped_at: datetime
    extra_data: Optional[Dict[str, Any]] = None  # renamed from 'metadata'

    class Config:
        from_attributes = True


class ModelImageResponse(BaseModel):
    id: int
    name: str
    file_url: str
    thumbnail_url: Optional[str]
    is_custom: bool
    uploaded_at: datetime

    class Config:
        from_attributes = True


class BackgroundResponse(BaseModel):
    id: int
    name: str
    file_url: str
    thumbnail_url: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ActionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    duration: float
    is_active: bool
    preview_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceTemplateResponse(BaseModel):
    id: int
    name: str
    emotion: EmotionType
    is_custom: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VideoJobResponse(BaseModel):
    id: int
    job_id: str
    status: VideoStatus
    progress: float
    error_message: Optional[str]
    output_video_url: Optional[str]
    processing_time: Optional[float]
    created_at: datetime
    completed_at: Optional[datetime]
    config: Dict[str, Any]

    class Config:
        from_attributes = True
