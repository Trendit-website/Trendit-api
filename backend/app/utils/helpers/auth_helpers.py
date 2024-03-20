'''
This module defines helper functions for handling 
authorization and authentication in the Trendit³ Flask application.

These functions assist with tasks such as code generation, 
saving password reset token, and saving 2FA token

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import random
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from app.extensions import db
from app.models.user import OneTimeToken
from app.utils.helpers.basic_helpers import console_log


def generate_six_digit_code():
    six_digit_code = int(random.randint(100000, 999999))
    
    console_log('SIX DIGIT CODE', six_digit_code)
    return six_digit_code


def send_code_async_email(app, user_email, six_digit_code, code_type):
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
        msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)
        
        if code_type == 'pwd_reset':
            subject = 'Reset your password'
            template = render_template("email/pwd_reset2.html", verification_code=six_digit_code, user_email=user_email)
            msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)
        elif code_type == '2FA':
            subject = 'One Time Password'
            template = render_template("email/otp.html", verification_code=six_digit_code, user_email=user_email)
            msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)

        elif code_type == 'welcome':
            subject = 'Welcome'
            template = render_template("email/welcome.html", redirect_link='https://app.trendit3.com/', user_email=user_email)
            msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)
        
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

def send_code_to_phone(user_phone, six_digit_code, code_type='verify_email'):
    pass

def send_2fa_code(user_obj, two_factor_method, six_digit_code):
    if two_factor_method == 'email':
        send_code_to_email(user_obj.email, six_digit_code, code_type='2FA') # send 2FA code to user's email
    elif two_factor_method == 'phone':
        # TODO: Implement Logic to send code to user's phone number. (For later when the platform grows)
        #send_code_to_phone(user_obj.profile.phone, six_digit_code, code_type='2FA') # send 2FA code to user's email
        pass
    elif two_factor_method == 'google_auth_app':
        pass
    else:
        pass

def save_pwd_reset_token(reset_token, user=None):
    try:
        if user is None:
            return None
        
        pwd_reset_token = OneTimeToken.query.filter(OneTimeToken.trendit3_user_id == user.id).first()
        if pwd_reset_token:
            pwd_reset_token.update(token=reset_token, used=False)
            return pwd_reset_token
        else:
            new_pwd_reset_token = OneTimeToken.create_token(token=reset_token, trendit3_user_id=user.id)
            return new_pwd_reset_token
    except Exception as e:
        console_log('RESET EXCEPTION', str(e))
        current_app.logger.error(f"An error occurred saving Reset token in the database: {str(e)}")
        db.session.rollback()
        db.session.close()
        return None


def save_2fa_token(two_FA_token, user=None):
    try:
        if user is None:
            return None
        
        two_fa_token = OneTimeToken.query.filter(OneTimeToken.trendit3_user_id == user.id).first()
        if two_fa_token:
            two_fa_token.update(token=two_FA_token, used=False)
            return two_fa_token
        else:
            new_two_fa_token = OneTimeToken.create_token(token=two_FA_token, trendit3_user_id=user.id)
            return new_two_fa_token
    except Exception as e:
        console_log('2FA EXCEPTION', str(e))
        current_app.logger.error(f"An error occurred saving the 2FA token in the database: {str(e)}")
        db.session.rollback()
        db.session.close()
        return None