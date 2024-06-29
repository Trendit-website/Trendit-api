'''
This module defines helper functions for managing users in the Trendit³ Flask application.

These functions assist with tasks such as:
    * fetching user info
    * checking if username or email exist
    * generating referral code. e.t.c...

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from enum import Enum
from threading import Thread
from flask import current_app
from werkzeug.datastructures import FileStorage
from sqlalchemy.exc import ( DataError, DatabaseError, SQLAlchemyError )

from ...extensions import db
from ...models.role import Role, RoleNames
from ...models.user import Trendit3User, Address, Profile
from ...models.pricing import Pricing
from ...models.notification import MessageStatus, MessageType, UserMessageStatus, Notification
from ...models.social import SocialMediaProfile
from ...utils.helpers.media_helpers import save_media
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.basic_helpers import generate_random_string


def async_save_profile_pic(app, user: Trendit3User, media_file):
    with app.app_context():
        try:
            user_profile = user.profile
            if isinstance(media_file, FileStorage) and media_file.filename != '':
                try:
                    profile_picture = save_media(media_file) # This saves image file, saves the path in db and return the Media instance
                except Exception as e:
                    log_exception(f"An error occurred saving profile image: {str(e)}")
            elif profile_picture == '' and user:
                if user_profile.profile_picture_id:
                    profile_picture = user_profile.profile_picture
                else:
                    profile_picture = None
            else:
                profile_picture = None
            
            user_profile.update(profile_picture=profile_picture)
        except Exception as e:
            log_exception()
            raise e

def save_profile_pic(user: Trendit3User, media_file: FileStorage):
    Thread(target=async_save_profile_pic, args=(current_app._get_current_object(), user, media_file)).start()


# for pricing icon
def async_save_pricing_icon(app, price_id, media_file):
    with app.app_context():
        session = db.session()
        try:
            price = session.query(Pricing).get(price_id)
            if price:
                if isinstance(media_file, FileStorage) and media_file.filename != '':
                    try:
                        price_icon = save_media(media_file)  # This saves image file, saves the path in db and return the Media instance
                    except Exception as e:
                        log_exception(f"An error occurred saving pricing icon: {str(e)}")
                        price_icon = None
                else:
                    price_icon = None

                price.update(price_icon=price_icon)
                session.commit()
        except Exception as e:
            session.rollback()
            log_exception()
            raise e
        finally:
            session.close()

def save_pricing_icon(price_id, media_file: FileStorage):
    Thread(target=async_save_pricing_icon, args=(current_app._get_current_object(), price_id, media_file)).start()


def add_user_role(role_name: Enum, user_id: int):
    try:
        user = Trendit3User.query.get(user_id)
        if not user:
            raise Exception("User not found")
        
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            raise Exception("Role not valid")
        
        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()
        
    except Exception as e:
        raise e

def get_user_info(user_id: int) -> dict:
    '''Gets profile details of a particular user'''
    
    if user_id is None:
        userInfo = {}
    else:
        trendit3_user = Trendit3User.query.get(user_id)
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


def get_trendit3_user_by_google_id(google_id):
    """
    Retrieves a Trendit3User object from the database based on social ID.

    Args:
        social_id: The social ID to search for.

    Returns:
        The Trendit3User object if found, or None if not found.
    """
    return Trendit3User.query.filter(Trendit3User.social_ids.google_id == google_id).first()


def get_trendit3_user_by_facebook_id(facebook_id):
    """
    Retrieves a Trendit3User object from the database based on social ID.

    Args:
        social_id: The social ID to search for.

    Returns:
        The Trendit3User object if found, or None if not found.
    """
    return Trendit3User.query.filter(Trendit3User.social_ids.facebook_id == facebook_id).first()


def get_trendit3_user_by_x_id(x_id):
    """
    Retrieves a Trendit3User object from the database based on social ID.

    Args:
        social_id: The social ID to search for.

    Returns:
        The Trendit3User object if found, or None if not found.
    """
    return Trendit3User.query.filter(Trendit3User.social_ids.x_id == x_id).first()


def get_trendit3_user_by_tiktok_id(tiktok_id):
    """
    Retrieves a Trendit3User object from the database based on social ID.

    Args:
        social_id: The social ID to search for.

    Returns:
        The Trendit3User object if found, or None if not found.
    """
    return Trendit3User.query.filter(Trendit3User.social_ids.tiktok_id == tiktok_id).first()

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


# @al-chris

def get_notifications(user_id:int, message_type=MessageType.NOTIFICATION):
    """
    Retrieve notifications for a user.

    Args:
        user_id (int): ID of the user for whom to retrieve notifications.
        message_type (MessageType): Type of the notifications to retrieve.
        status (MessageStatus): Status of the notifications to retrieve.

    Returns:
        list of Message: List of notifications matching the criteria.
    """
    
    if user_id is None:
        userNotifications = []
    else:
        trendit3_user = Trendit3User.query.filter(Trendit3User.id == user_id).first()
        notifications = trendit3_user.notifications
        print([notification.recipients for notification in Notification.query.all()])
        userNotifications = []

        for notification in notifications:
            if notification.type == message_type:
                notification_dict = notification.to_dict()
                noti_status = UserMessageStatus.query.filter_by(user_id=user_id, message_id=notification_dict['id']).first().status.value
                notification_dict['status'] = noti_status
                userNotifications.append(notification_dict)
    
    return userNotifications


def mark_as_read(user_id, message_id):
    """
    Mark a message as read for a user.

    Args:
        user_id (int): Id of the user who is marking the message as read.
        message_id (int): ID of the message to mark as read.
    """
    user_message_status = UserMessageStatus.query.filter_by(user_id=user_id, message_id=message_id).first()
    if user_message_status:
        user_message_status.status = MessageStatus.READ
        db.session.commit()

def get_social_profile(platform: str, user_id: int):
    try:
        profile = SocialMediaProfile.query.filter(SocialMediaProfile.platform==platform, SocialMediaProfile.trendit3_user_id==user_id).first()
        return profile
    except (DataError, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e