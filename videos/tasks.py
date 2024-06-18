from venv import logger
from celery import shared_task
from .utils import process_video

@shared_task
def process_video_task(video_path):
    try:
        processed_video_path = process_video(video_path)
        return processed_video_path
    except Exception as e:
        logger.error(f"Failed to process video {video_path}: {str(e)}")
        raise
