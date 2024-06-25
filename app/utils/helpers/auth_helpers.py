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
from enum import Enum

from app import mail
from config import Config
from ...extensions import db
from ...utils.helpers.basic_helpers import console_log, log_exception
from .mail_helpers import send_code_to_email
from ...models import Trendit3User, TempUser, OneTimeToken


class EmailType(Enum):
    VERIFY_EMAIL = 'verify_email'
    PWD_RESET = 'pwd_reset'
    TWO_FA = '2FA'
    WELCOME = 'welcome'
    TASK_APPROVED = 'task_approved'
    TASK_REJECTED = 'task_rejected'
    CREDIT = 'credit'
    DEBIT = 'debit'


def generate_six_digit_code():
    six_digit_code = int(random.randint(100000, 999999))
    
    console_log('SIX DIGIT CODE', six_digit_code)
    return six_digit_code



def send_2fa_code(user, two_factor_method, six_digit_code):
    if two_factor_method == 'email':
        send_code_to_email(user.email, six_digit_code, code_type='2FA') # send 2FA code to user's email
    
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