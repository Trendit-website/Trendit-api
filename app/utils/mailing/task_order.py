from flask import Flask
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User, Task


def send_async_task_order_review(app: Flask, task_id: int) -> None:
    with app.app_context():
        task_order: Task = Task.query.filter_by(id=task_id)
        user: Trendit3User = task_order.trendit3_user
        user_email = user.email
        
        subject = "Task Order In Review"
        template = render_template(
            "mail/task-order-review.html",
            user=user,
            user_email=user_email,
            task_order=task_order
        )
        msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING TASK ORDER REVIEW MAIL", e)

def send_task_order_review_email(task_id) -> None:
    
    Thread(target=send_async_task_order_review, args=(current_app._get_current_object(), task_id)).start()
