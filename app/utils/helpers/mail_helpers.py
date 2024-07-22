from flask import Flask
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from enum import Enum

from app import mail
from config import Config
from ...utils.payments.rates import convert_amount
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User, SocialMediaProfile, SocialLinkStatus, TaskPerformance

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
        user = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        username = user.username if user else ''
        firstname = user.profile.firstname if user else ''
        
        subject = 'Verify Your Email'
        template = render_template("mail/verify-email.html", verification_code=six_digit_code)
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        if code_type == 'pwd_reset':
            subject = 'Reset your password'
            template = render_template(
                "mail/forgot-password.html",
                reset_url=six_digit_code,
                user_email=user_email,
                user=user,
                firstname=firstname,
                username=username)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif code_type == '2FA':
            subject = 'One Time Password'
            template = render_template(
                "mail/otp.html",
                verification_code=six_digit_code,
                user_email=user_email,
                user=user,
                firstname=firstname)
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
def send_async_other_email(app, user_email, email_type, task_type, task_time, task_description, amount=None, admin_login_code=None):
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
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        if email_type == 'welcome':
            subject = 'Welcome'
            template = render_template("mail/welcome.html", redirect_link=f"{Config.APP_DOMAIN_NAME}", user_email=user_email, firstname=firstname, username=username)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

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
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'task_rejected':
            subject = 'Task Rejected'
            template = render_template(
                "mail/task-rejection.html",
                redirect_link=f"{Config.APP_DOMAIN_NAME}",
                user_email=user_email,
                firstname=firstname,
                username=username
            )
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

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
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

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
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'new_admin':
            subject = 'Admin Approved'
            template = render_template(
                "email/new_admin.html",
                redirect_link='https://admin.trendit3.com/',
                user_email=user_email,
                firstname=firstname,
                username=username,
                amount=amount)
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        elif email_type == 'admin_login':
            subject = 'Admin Login'
            template = render_template(
                "email/admin_login.html",
                redirect_link=f'https://admin.trendit3.com/verify-login?token={admin_login_code}',
                firstname=firstname,
                user_email=user_email
            )
            msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)

        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception('EXCEPTION SENDING MAIL', e)
            console_log('EXCEPTION SENDING MAIL', f'An error occurred while sending the {email_type} email type: {str(e)}')


def send_other_emails(user_email, email_type='membership', task_type=None, task_time=None, task_description=None, amount=None, admin_login_code=''):
    Thread(target=send_async_other_email, args=(current_app._get_current_object(), user_email, email_type, task_type, task_time, task_description, amount, admin_login_code)).start()



def send_async_transaction_alert_email(app: Flask, tx_type: str, user_email: str, reason: str, amount=None) -> None:
    with app.app_context():
        user: Trendit3User = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        username: str = user.username if user else ''
        firstname: str = user.profile.firstname if user else ''
        currency_code: str = user.wallet.currency_code
        amount: str = convert_amount(amount, currency_code)
        
        console_log("amount", f"{currency_code} {amount}")
        
        subject = 'Wallet Debited'
        template = render_template(
            "mail/debit-alert.html",
            user=user,
            user_email=user_email,
            username=username,
            currency_code=currency_code,
            amount=amount,
            reason=reason
        )
        if tx_type == "credit":
            subject = 'Wallet Credited'
            template = render_template(
                "mail/credit-alert.html",
                user=user,
                user_email=user_email,
                firstname=firstname,
                username=username,
                currency_code=currency_code,
                amount=amount,
                reason=reason
            )
        
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING '{tx_type} transaction' MAIL", e)

def send_transaction_alert_email(user_email, reason, amount, tx_type="debit"):
    Thread(target=send_async_transaction_alert_email, args=(current_app._get_current_object(), tx_type, user_email, reason, amount)).start()

def send_async_social_profile_status_email(app: Flask, user_email, platform, status):
    with app.app_context():
        user: Trendit3User = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        social_profile: SocialMediaProfile = SocialMediaProfile.query.filter_by(platform=platform, trendit3_user_id=user.id).first()
        
        console_log("social_profile", social_profile)
        
        subject = "Social Profile Rejected"
        template = render_template(
            "mail/social-rejection.html",
            user=user,
            user_email=user_email,
            social_profile=social_profile
        )
        if status == SocialLinkStatus.VERIFIED:
            subject = "Social Profile Approved"
            template = render_template(
                "mail/social-approval.html",
                user=user,
                user_email=user_email,
                social_profile=social_profile
            )
        
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING MAIL FOR {status} SOCIAL PROFILE", e)

def send_social_profile_status_email(user_email, platform, status=SocialLinkStatus.REJECTED) -> None:
    '''
    Asynchronously sends an email about the state of a submitted social profile.

    This function runs in a separate thread and sends an email to the user.

    Args:
        status (str): the status of the social profile (SocialLinkStatus.VERIFIED or SocialLinkStatus.REJECTED)
        user_email (str): The email address of the user.

    Returns:
        None
    '''
    
    Thread(target=send_async_social_profile_status_email, args=(current_app._get_current_object(), user_email, platform, status)).start()




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
        
        msg = Message(subject, sender=Config.MAIL_DEFAULT_SENDER, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING MAIL FOR {performed_task.status} TASK PERFORMANCE", e)

def send_task_performance_email(pt_id) -> None:
    
    Thread(target=send_async_task_performance_email, args=(current_app._get_current_object(), pt_id)).start()
