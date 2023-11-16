from app.extensions import db
from app.models.user import Trendit3User, Address, Profile
from app.utils.helpers.basic_helpers import generate_random_string


def get_user_info(userId):
    '''Gets profile details of a particular user'''
    
    if userId is None:
        userInfo = {}
    else:
        trendit3_user = Trendit3User.query.filter(Trendit3User.id == userId).first()
        userInfo = trendit3_user.to_dict()
    
    for key in userInfo:
        if userInfo[key] is None:
            userInfo[key] = ''
    
    return userInfo


def is_username_exist(username, user=None):
    if user:
        # Query the database to check if the email is available, excluding the user's own email
        Trendit3_user = Trendit3User.query.filter(Trendit3User.username == username, Trendit3User.id != user.id).first()
    else:
        Trendit3_user = Trendit3User.query.filter(Trendit3User.username == username).first()
        
    if Trendit3_user is None:
        return False
    else:
        return True


def is_email_exist(email, user=None):
    Trendit3_user = None
    
    if user:
        # Query the database to check if the email is available, excluding the user's own email
        Trendit3_user = Trendit3User.query.filter(Trendit3User.email == email, Trendit3User.id != user.id).first()
    else:
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
        return None


def generate_referral_code(length=6):
    while True:
        code = generate_random_string(length)
        # Check if the code already exists in the database
        if not referral_code_exists(code):
            return code

def referral_code_exists(code):
    profile = Profile.query.filter(Profile.referral_code == code).first()
    if profile:
        return True
    return False