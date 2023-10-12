import random
from app.models.user import Trendit3User
from app import mail
from flask_mail import Message


def is_username_exist(username):
    Trendit3_user = Trendit3User.query.filter(Trendit3User.username == username).first()
    if Trendit3_user is None:
        return False
    else:
        return True
    
def is_email_exist(email):
    Trendit3_user = Trendit3User.query.filter(Trendit3User.email == email).first()
    if Trendit3_user is None:
        return False
    else:
        return True

def get_trendit3_user(email_username):
    # get user from db with the email or username.
    if is_username_exist(email_username):
        return Trendit3User.query.filter(Trendit3User.username == email_username).first()
    elif is_email_exist(email_username):
        return Trendit3User.query.filter(Trendit3User.email == email_username).first()
    else:
        return False

def generate_email_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(user_email, verification_code):
    msg = Message('Verify Your Email', sender='olowu2018@mail.com', recipients=[user_email])
    msg.body = f'Your verification code is: {verification_code}'
    mail.send(msg)
