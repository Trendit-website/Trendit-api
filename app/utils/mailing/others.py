from flask import Flask
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User


# SEND OTHER EMAILS LIKE WELCOME MAIL, CREDIT ALERT, ETC
def send_async_other_email(app: Flask, user_email: str, email_type: str, task_type: str | None, task_time, task_description, amount=None, admin_login_code=None):
    """
    Sends an email asynchronously.

    This function runs in a separate thread and sends an email to the user. 
    It uses the Flask application context to ensure the mail object works correctly.

    Args:
        app (Flask): The Flask application instance.
        user_email (str): The email address of the user.
        email_type (str): The type of the email ('welcome', 'task_approved', 'task_rejected', 'credit', 'debit').

    Returns:
        None
    """
    
    with app.app_context():
        user = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        username = user.username if user else ''
        firstname = user.profile.firstname if user else ''
        
        subject = 'membership'
        template = render_template("mail/membership-paid.html", redirect_link=f"{Config.APP_DOMAIN_NAME}", user_email=user_email, username=username)
        msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)
        
        if email_type == 'welcome':
            subject = 'Welcome'
            template = render_template("mail/welcome.html", redirect_link=f"{Config.APP_DOMAIN_NAME}", user_email=user_email, firstname=firstname, username=username)
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        elif email_type == 'task_approved':
            subject = 'Task Approved'
            template = render_template(
                "mail/task-approval.html", 
                redirect_link=f"{Config.APP_DOMAIN_NAME}", 
                user_email=user_email,
                firstname=firstname, 
                username=username,
                task_type=task_type,
                task_time=task_time,
                task_description=task_description
            )
            print(task_description, task_time, task_type)
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        elif email_type == 'task_rejected':
            subject = 'Task Rejected'
            template = render_template(
                "mail/task-rejection.html",
                redirect_link=f"{Config.APP_DOMAIN_NAME}",
                user_email=user_email,
                firstname=firstname,
                username=username
            )
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        elif email_type == 'credit':
            subject = 'Account Credited'
            template = render_template(
                "email/credit-alert.html",
                redirect_link=f"{Config.APP_DOMAIN_NAME}",
                user_email=user_email,
                firstname=firstname,
                username=username,
                amount=amount
            )
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        elif email_type == 'debit':
            subject = 'Account Debited'
            template = render_template(
                "mail/debit-alert.html",
                redirect_link=f"{Config.APP_DOMAIN_NAME}",
                user_email=user_email,
                firstname=firstname,
                username=username,
                amount=amount
            )
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        elif email_type == 'new_admin':
            subject = 'Admin Approved'
            template = render_template(
                "email/new_admin.html",
                redirect_link='https://admin.trendit3.com/',
                user_email=user_email,
                firstname=firstname,
                username=username,
                amount=amount)
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        elif email_type == 'admin_login':
            subject = 'Admin Login'
            template = render_template(
                "email/admin_login.html",
                redirect_link=f'https://admin.trendit3.com/verify-login?token={admin_login_code}',
                firstname=firstname,
                user_email=user_email
            )
            msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)

        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception('EXCEPTION SENDING MAIL', e)
            console_log('EXCEPTION SENDING MAIL', f'An error occurred while sending the {email_type} email type: {str(e)}')


def send_other_emails(user_email, email_type='membership', task_type=None, task_time=None, task_description=None, amount=None, admin_login_code=''):
    Thread(target=send_async_other_email, args=(current_app._get_current_object(), user_email, email_type, task_type, task_time, task_description, amount, admin_login_code)).start()
