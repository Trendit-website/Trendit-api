from flask import Flask
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User, TaskPerformance


def send_async_task_performance_email(app: Flask, pt_id):
    with app.app_context():
        performed_task: TaskPerformance = TaskPerformance.query.filter_by(id=pt_id)
        user: Trendit3User = performed_task.trendit3_user
        user_email = user.email
        
        subject = "Task Performance Rejected"
        template = render_template(
            "mail/task-performance-rejection.html",
            user=user,
            user_email=user_email,
            performed_task=performed_task
        )
        if performed_task.status == "completed":
            subject = "Task Performance Accepted"
            template = render_template(
                "mail/task-performance-approval.html",
                user=user,
                user_email=user_email,
                performed_task=performed_task
            )
        
        msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING MAIL FOR {performed_task.status} TASK PERFORMANCE", e)

def send_task_performance_email(pt_id) -> None:
    
    Thread(target=send_async_task_performance_email, args=(current_app._get_current_object(), pt_id)).start()
