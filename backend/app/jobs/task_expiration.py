import logging
from datetime import datetime, timedelta

from app.extensions import db, celery
from app.models.task import TaskPerformance

@celery.task
def check_task_status(task_id):
    # Fetch the task performance instance
    task_performance = TaskPerformance.query.get(task_id)

    # If the task is still pending and it's been more than an hour since it started
    if task_performance.status == 'pending' and datetime.utcnow() > task_performance.started_at + timedelta(hours=1):
        # Mark the task as failed
        task_performance.status = 'failed'
        logging.info(f'Task performance of ID {task_performance.id} expired and status updated to failed')
        db.session.commit()
    