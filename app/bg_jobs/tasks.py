from datetime import datetime, timedelta
from celery import shared_task

from ..extensions import db
from ..models import TaskPerformance
from ..utils.helpers.basic_helpers import log_exception
from ..utils.helpers.media_helpers import save_media


@shared_task(bind=True)
def save_task_media_files(self, app, task_id_key: str | int, media_files):
    with app.app_context():
        try:
            from ..utils.helpers.task_helpers import fetch_task
            task = fetch_task(task_id_key)
            
            #save media files
            task_media = []
            if media_files:
                for media_file in media_files:
                    media = save_media(media_file)
                    task.media.append(media)
            elif not media_files and task:
                task.media = task.media
            
            db.session.commit()
        except Exception as e:
            log_exception("an exception occurred saving task media", e)
            raise e


@shared_task
def check_expired_tasks():
    pending_tasks = TaskPerformance.query.filter_by(status='pending').all()
    for task in pending_tasks:
        if task.started_at < datetime.utcnow() - timedelta(hours=1):
            task.update(status='failed')
            db.session.commit()