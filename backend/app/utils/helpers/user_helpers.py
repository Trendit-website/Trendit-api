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


def is_user_exist(identifier, field, user=None):
    """
    Checks if a user exists in the database with the given identifier and field.

    Args:
        identifier: The identifier to search for (email or username).
        field: The field to search in ("email" or "username").
        user: An optional user object. If provided, the check excludes the user itself.

    Returns:
        True if the user exists, False otherwise.
    """
    base_query = Trendit3User.query.filter(getattr(Trendit3User, field) == identifier)
    if user:
        base_query = base_query.filter(Trendit3User.id != user.id)
    return base_query.scalar() is not None

def is_username_exist(username, user=None):
    """
    Checks if a username exists in the database, excluding the current user if provided.

    Args:
        username: The username to search for.
        user: An optional user object. If provided, the check excludes the user itself.

    Returns:
        True if the username is already taken, False if it's available.
    """
    base_query = Trendit3User.query.filter(Trendit3User.username == username)
    if user:
        # Query the database to check if the username is available, excluding the user's own username
        base_query = base_query.filter(Trendit3User.id != user.id)
    
    return base_query.scalar() is not None


def is_email_exist(email, user=None):
    """
    Checks if an email address exists in the database, excluding the current user if provided.

    Args:
        email: The email address to search for.
        user: An optional user object. If provided, the check excludes the user itself.

    Returns:
        True if the email address is already taken, False if it's available.
    """
    base_query = Trendit3User.query.filter(Trendit3User.email == email)
    if user:
        # Query the database to check if the email is available, excluding the user's own email
        base_query = base_query.filter(Trendit3User.id != user.id)
    
    return base_query.scalar() is not None


def get_trendit3_user(email_username):
    """
    Retrieves a Trendit3User object from the database based on email or username.

    Args:
        email_username: The email address or username to search for.

    Returns:
        The Trendit3User object if found, or None if not found.
    """
    
    user = Trendit3User.query.filter(Trendit3User.email == email_username).first()
    if user:
        return user
    
    return Trendit3User.query.filter(Trendit3User.username == email_username).first()



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