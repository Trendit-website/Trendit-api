from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from celery import Celery
from celery.schedules import crontab

from config import Config

db = SQLAlchemy()
mail = Mail()

celery = Celery()

celery.conf.beat_schedule = {
    'check-task-timeouts-every-hour': {
        'task': 'app.jobs.check_task_timeouts',
        'schedule': crontab(minute=0),
    },
}
