from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from enum import Enum

from app import mail
from config import Config
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User

class EmailType(Enum):
    VERIFY_EMAIL = 'verify_email'
    PWD_RESET = 'pwd_reset'
    TWO_FA = '2FA'
    WELCOME = 'welcome'
    TASK_APPROVED = 'task_approved'
    TASK_REJECTED = 'task_rejected'
    CREDIT = 'credit'
    DEBIT = 'debit'

# SEND VERIFICATION CODE TO USER'S EMAIL
def send_code_async_email(app, user_email:str, six_digit_code:int | str, code_type:str):
    """
    Sends an email asynchronously.

    This function runs in a separate thread and sends an email to the user. 
    It uses the Flask application context to ensure the mail object works correctly.

    Args:
        app (Flask): The Flask application instance.
        user_email (str): The email address of the user.
        six_digit_code (str): The six-digit code to include in the email.
        code_type (str): The type of the code ('verify_email', 'pwd_reset', '2FA').

    Returns:
        None
    """
    with app.app_context():
        subject = 'Verify Your Email'
        template = render_template("email/verify_email2.html", verification_code=six_digit_code)
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        user = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        username = user.username if user else ''
        
        if code_type == 'pwd_reset':
            subject = 'Reset your password'
            template = render_template("email/pwd_reset2.html", reset_url=six_digit_code, user_email=user_email, username=username)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif code_type == '2FA':
            subject = 'One Time Password'
            template = render_template("email/otp.html", verification_code=six_digit_code, user_email=user_email)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        try:
            mail.send(msg)
        except Exception as e:
            console_log('EXCEPTION SENDING MAIL', f'An error occurred while sending the {code_type} code: {str(e)}')


def send_code_to_email(user_email, six_digit_code, code_type='verify_email'):
    """
    Sends a code to the user's email address in a new thread.

    This function creates a new thread and calls the send_code_async_email function in it. 
    This allows the rest of the application to continue running while the email is being sent.

    Args:
        user_email (str): The email address of the user.
        six_digit_code (str): The six-digit code to include in the email.
        code_type (str, optional): The type of the code ('verify_email', 'pwd_reset', '2FA'). 
                                    Defaults to 'verify_email'.

    Returns:
        None
    """
    Thread(target=send_code_async_email, args=(current_app._get_current_object(), user_email, six_digit_code, code_type)).start()

def send_url_to_email (user_email: str, url: str, code_type:str = 'pwd_reset'):
    Thread(target=send_code_async_email, args=(current_app._get_current_object(), user_email, url, code_type)).start()


# SEND OTHER EMAILS LIKE WELCOME MAIL, CREDIT ALERT, ETC
def send_async_other_email(app, user_email, email_type, amount=None, admin_login_code=None):
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
        
        subject = 'membership'
        template = render_template("email/membership_paid2.html", redirect_link='https://app.trendit3.com/', user_email=user_email, username=username)
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        if email_type == 'welcome':
            subject = 'Welcome'
            template = render_template("email/welcome.html", redirect_link='https://app.trendit3.com/', user_email=user_email, username=username)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'task_approved':
            subject = 'Task Approved'
            template = render_template("email/task_approved.html", redirect_link='https://app.trendit3.com/', user_email=user_email, username=username)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'task_rejected':
            subject = 'Task Rejected'
            template = render_template("email/task_rejected.html", redirect_link='https://app.trendit3.com/', user_email=user_email, username=username)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'credit':
            subject = 'Account Credited'
            template = render_template("email/credit_alert.html", redirect_link='https://app.trendit3.com/', user_email=user_email, username=username, amount=amount)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'debit':
            subject = 'Account Debited'
            template = render_template("email/debit_alert.html", redirect_link='https://app.trendit3.com/', user_email=user_email, username=username, amount=amount)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'new_admin':
            subject = 'Admin Approved'
            template = render_template("email/new_admin.html", redirect_link='https://admin.trendit3.com/', user_email=user_email, username=username, amount=amount)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'admin_login':
            subject = 'Admin Login'
            template = render_template("email/admin_login.html", redirect_link=f'https://admin.trendit3.com/verify-login?token={admin_login_code}', user_email=user_email)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception('EXCEPTION SENDING MAIL', e)
            console_log('EXCEPTION SENDING MAIL', f'An error occurred while sending the {email_type} email type: {str(e)}')


def send_other_emails(user_email, email_type='membership', amount=None, admin_login_code=None):
    Thread(target=send_async_other_email, args=(current_app._get_current_object(), user_email, email_type, amount, admin_login_code)).start()