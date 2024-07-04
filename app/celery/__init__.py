'''
This package contains the celery extension and background jobs for the Trendit³ Flask application.

It the make_celery function that could be used with the app factory pattern
It includes jobs for updating pending social tasks, sending notifications, and others

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask import Flask
from celery import Celery, Task
from celery.schedules import crontab

from config import Config

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    
    
    celery_app = Celery(app.name, task_cls=ContextTask)
    celery_app.config_from_object(app.config["CELERY_CONFIG"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    
    return celery



def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app