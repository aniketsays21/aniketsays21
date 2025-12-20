from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON, Text, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import enum
from config.settings import settings

# Create engine
# SQLite doesn't support pool_size/max_overflow, so only use them for other databases
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class VideoStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EmotionType(str, enum.Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SURPRISED = "surprised"


# Models
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    price = Column(String, nullable=True)
    images = Column(JSON)  # List of image URLs
    scraped_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)  # renamed from 'metadata' (reserved word)


class ModelImage(Base):
    __tablename__ = "model_images"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_path = Column(String)
    file_url = Column(String)
    thumbnail_url = Column(String, nullable=True)
    is_custom = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)  # renamed from 'metadata'


class Background(Base):
    __tablename__ = "backgrounds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_path = Column(String)
    file_url = Column(String)
    thumbnail_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Action(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    pose_sequence = Column(JSON)  # Pose keypoints or animation data
    duration = Column(Float)  # in seconds
    is_active = Column(Boolean, default=True)
    preview_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class VoiceTemplate(Base):
    __tablename__ = "voice_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    file_path = Column(String, nullable=True)  # For cloned voices
    voice_id = Column(String, nullable=True)  # For API-based voices
    emotion = Column(Enum(EmotionType), default=EmotionType.NEUTRAL)
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)

    # References
    product_id = Column(Integer, nullable=True)
    model_image_id = Column(Integer)
    background_id = Column(Integer)
    action_id = Column(Integer)
    voice_template_id = Column(Integer, nullable=True)

    # Configuration
    audio_text = Column(Text, nullable=True)
    audio_file_path = Column(String, nullable=True)
    emotion = Column(Enum(EmotionType), default=EmotionType.NEUTRAL)
    duration = Column(Float)

    # Status
    status = Column(Enum(VideoStatus), default=VideoStatus.PENDING)
    progress = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)

    # Output
    output_video_path = Column(String, nullable=True)
    output_video_url = Column(String, nullable=True)

    # Metadata
    config = Column(JSON)  # Full configuration for reproducibility
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


# Database utilities
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
