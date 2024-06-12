from datetime import datetime, timedelta
from celery import shared_task

from app.extensions import db
from app.models import TaskPerformance

from .. import create_app
from ..utils.helpers.task_helpers import fetch_task
from ..utils.helpers.media_helpers import save_media
from ..utils.helpers.basic_helpers import log_exception

app = create_app()


@shared_task
def check_expired_tasks():
    pending_tasks = TaskPerformance.query.filter_by(status='pending').all()
    for task in pending_tasks:
        if task.started_at < datetime.utcnow() - timedelta(hours=1):
            task.update(status='failed')
            db.session.commit()