from datetime import datetime, timedelta
from celery import shared_task

from app.extensions import db
from app.models import TaskPerformance


@shared_task
def check_expired_tasks():
    pending_tasks = TaskPerformance.query.filter_by(status='pending').all()
    for task in pending_tasks:
        if task.started_at < datetime.utcnow() - timedelta(hours=1):
            task.update(status='failed')
            db.session.commit()
