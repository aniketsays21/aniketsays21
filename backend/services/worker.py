from celery import Celery
from config.settings import settings
import asyncio

# Create Celery app
celery_app = Celery(
    "ugc_video_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.JOB_TIMEOUT,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)


@celery_app.task(name="generate_video")
def generate_video_task(job_id: str):
    """
    Celery task for video generation
    Runs the async video processing function
    """
    from services.video_service import process_video_job

    # Run async function in event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_video_job(job_id))

    return {"job_id": job_id, "status": "completed"}
