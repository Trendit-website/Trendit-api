from datetime import datetime, timedelta
from celery import shared_task
from flask import current_app

from run import celery
from ...extensions import db
from ...models import TaskPerformance
from ...utils.helpers.basic_helpers import log_exception, console_log
from ...utils.helpers.media_helpers import save_media


@celery.shared_task(bind=True)
def save_task_media_files(self, task_id_key: str | int, media_file_paths):
    try:
        with current_app.app_context():
            console_log("celery saving media", f"starting... {media_file_paths}")
            from ...utils.helpers.task_helpers import fetch_task
            task = fetch_task(task_id_key)
            
            if task:
                #save media files
                if media_file_paths:
                    for media_file_path in media_file_paths:
                        with open(media_file_path, 'rb') as media_file:
                            console_log("media_file", media_file)
                            media = save_media(media_file)
                            console_log("media saved", media)
                            task.media.append(media)
                elif not media_file_paths and task:
                    task.media = task.media
            
                db.session.commit()
                console_log("end of celery task...", "...")
    except Exception as e:
        log_exception("an exception occurred saving task media", e)
        db.session.rollback()
        raise e
    finally:
        db.session.close()


@shared_task(bind=True)
def check_expired_tasks():
    pending_tasks = TaskPerformance.query.filter_by(status='pending').all()
    for task in pending_tasks:
        if task.started_at < datetime.utcnow() - timedelta(hours=1):
            task.update(status='failed')
            db.session.commit()