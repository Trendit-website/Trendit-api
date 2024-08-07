"""
This package contains functions for sending emails using Flask-Mail.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Estate Management
"""

from flask import Flask
from flask_mail import Message

from app import mail
from ..helpers.basic_helpers import log_exception

from .others import send_other_emails
from .task_order import send_task_order_review_email
from .transactions import send_transaction_alert_email
from .codes import send_code_to_email, send_url_to_email
from .task_performance import send_task_performance_email
from .social_profiles import send_social_profile_status_email


def send_async_email(app: Flask, msg: Message) -> None:
    """
    Send an email asynchronously.

    :param app: The Flask application instance.
    :param msg: The email message to be sent.
    """
    with app.app_context():
        
        try:
            mail.send(msg)
        except Exception as e:
            raise e
            log_exception('EXCEPTION SENDING MAIL', e)

