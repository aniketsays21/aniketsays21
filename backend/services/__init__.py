# Only import scraper_service for local development
# Other services require heavy dependencies (celery, PIL, etc.)
from . import scraper_service

__all__ = [
    "scraper_service",
]

# Lazy imports for other services - uncomment when dependencies are installed:
# from . import model_service
# from . import background_service
# from . import voice_service
# from . import video_service
# from . import worker
