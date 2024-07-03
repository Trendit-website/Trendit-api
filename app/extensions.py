'''
This module initializes the extensions used in the Trendit³ Flask application.

It sets up SQLAlchemy, Flask-Mail, and Celery with the configurations defined in the Config class.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from celery import Celery
from celery.schedules import crontab
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config

db = SQLAlchemy()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    
    from app.bg_jobs.tasks import save_task_media_files
    
    return celery
