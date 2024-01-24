from celery import Celery
from datetime import datetime, timedelta

from config import Config
from app.models.task import TaskPerformance

celery_app = Celery(
    'background_tasks',
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    accept_content=['application/json'],
    task_serializer='json',
    result_serializer='json'
)

@celery_app.task
def update_pending_tasks():
    pending_performances = TaskPerformance.query.filter_by(status='pending').all()
    for performance in pending_performances:
        if performance.started_at < datetime.utcnow() - timedelta(hours=1):
            performance.update(status='failed')