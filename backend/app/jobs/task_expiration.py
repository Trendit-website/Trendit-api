import logging
from flask import current_app
from datetime import datetime, timedelta

from app.extensions import db, celery
from app.models.task import TaskPerformance

@celery.task
def check_tasks_status():
    now = datetime.utcnow()
    timeout_threshold = now - timedelta(hours=1)
    timed_out_tasks = TaskPerformance.query.filter(
        TaskPerformance.status == 'pending',
        TaskPerformance.started_at <= timeout_threshold
    ).all()
    for task in timed_out_tasks:
        task.status = 'timed_out'
        logging.info(f'Task performance with ID{task.id}, expired and status updated to timed_out')
    db.session.commit()
