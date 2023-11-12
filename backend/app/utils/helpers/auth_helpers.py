import random, sys
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from app.extensions import db
from app.models.user import PwdResetToken
from app.utils.helpers.basic_helpers import console_log


def generate_email_verification_code():
    verification_code = int(random.randint(100000, 999999))
    
    console_log('VERIFICATION CODE', verification_code)
    return verification_code

def send_code_to_email(user_email, verification_code, code_type='verify_email'):
    
    subject = 'Verify Your Email'
    template = render_template("email/verify_email.html", verification_code=verification_code)
    msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)
    
    if code_type == 'pwd_reset':
        subject = 'Reset your password'
        template = render_template("email/pwd_reset.html", verification_code=verification_code, user_email=user_email)
        msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)
    
    mail.send(msg)

def save_pwd_reset_token(reset_token, user=None):
    try:
        if user is None:
            return None
        
        pwd_reset_token = PwdResetToken.query.filter(PwdResetToken.trendit3_user_id == user.id).first()
        if pwd_reset_token:
            pwd_reset_token.update(reset_token=reset_token, used=False)
            return pwd_reset_token
        else:
            new_pwd_reset_token = PwdResetToken.create_token(reset_token=reset_token, trendit3_user_id=user.id)
            return new_pwd_reset_token
    except Exception as e:
        current_app.logger.error(f"An error occurred saving Reset token in the database: {str(e)}")
        db.session.rollback()
        db.session.close()
        return None