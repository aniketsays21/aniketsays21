from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI UGC Video Platform"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40

    # Redis
    REDIS_URL: str
    REDIS_CACHE_DB: int = 1

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Storage
    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 52428800

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""

    # AI Models
    USE_LOCAL_MODELS: bool = True
    MODEL_CACHE_DIR: str = "./model_cache"

    # Video Generation
    VIDEO_MODEL: str = "magicanimate"
    VIDEO_RESOLUTION: str = "512x512"
    VIDEO_FPS: int = 24
    VIDEO_DURATION: int = 5
    MAX_VIDEO_DURATION: int = 30

    # Replicate API
    REPLICATE_API_TOKEN: str = ""

    # Voice Synthesis
    VOICE_MODEL: str = "bark"
    BARK_MODEL_SIZE: str = "small"
    ENABLE_VOICE_CLONING: bool = True

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""

    # Background Removal
    BG_REMOVAL_MODEL: str = "rembg"
    SAM_MODEL_TYPE: str = "vit_h"

    # Scraping
    PLAYWRIGHT_HEADLESS: bool = True
    SCRAPING_TIMEOUT: int = 30000
    MAX_IMAGES_PER_PRODUCT: int = 10
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_API_KEY: str = ""  # ScraperAPI key for bypassing anti-bot protection

    # Apify
    APIFY_API_TOKEN: str = ""  # Apify API token for product scraping
    APIFY_SHOPIFY_ACTOR: str = "linen_snack~shopify-product-scraper-extract-product-data-via-json-api"
    APIFY_ECOMMERCE_ACTOR: str = "apify~e-commerce-scraping-tool"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""

    # Features
    ENABLE_ANALYTICS: bool = False
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 3600

    # GPU Settings
    CUDA_VISIBLE_DEVICES: str = "0"
    ENABLE_GPU: bool = True
    GPU_MEMORY_FRACTION: float = 0.8

    # Queue Settings
    MAX_CONCURRENT_JOBS: int = 3
    JOB_TIMEOUT: int = 600

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
