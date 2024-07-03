'''
This package contains the Celery background jobs for the Trendit³ Flask application.

It includes jobs for updating pending social tasks, sending notifications, and others

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from celery import shared_task
