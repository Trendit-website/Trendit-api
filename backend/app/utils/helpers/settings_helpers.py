'''
This module defines helper functions for handling 
user settings in the Trendit³ Flask application.

These functions assist with tasks such as updating notification preference, 
update security preference, and updating UI appearance preference.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from sqlalchemy.exc import ( DataError, DatabaseError )
from werkzeug.security import generate_password_hash
from flask_jwt_extended import get_jwt_identity

from ...models import Trendit3User, SecuritySetting
from ...exceptions import InvalidTwoFactorMethod


def update_notification_preferences(notification_preference: object, data: dict):
    """
    Update notification preferences based on the provided data.
    
    Args:
        notification_preference (object): The NotificationPreference db object to be updated.
        data (dict): Dictionary containing notification preference data.
            It should be in the format:
            {
                "email": {
                    "new_features": True,
                    "new_tasks": False,
                    "money_earned": True
                },
                "in_app": {
                    "new_features": True,
                    "new_tasks": True,
                    "money_earned": True
                },
                "push": {
                    "new_features": False,
                    "new_tasks": False,
                    "money_earned": False
                }
            }
    """
    try:
        email_data = data.get('email', {})
        in_app_data = data.get('in_app', {})
        push_data = data.get('push', {})
        
        notification_preference.update(
            email_new_features=email_data.get('new_features', notification_preference.email_new_features),
            email_new_tasks=email_data.get('new_tasks', notification_preference.email_new_tasks),
            email_money_earned=email_data.get('money_earned', notification_preference.email_money_earned),
            in_app_new_features=in_app_data.get('new_features', notification_preference.in_app_new_features),
            in_app_new_tasks=in_app_data.get('new_tasks', notification_preference.in_app_new_tasks),
            in_app_money_earned=in_app_data.get('money_earned', notification_preference.in_app_money_earned),
            push_new_features=push_data.get('new_features', notification_preference.push_new_features),
            push_new_tasks=push_data.get('new_tasks', notification_preference.push_new_tasks),
            push_money_earned=push_data.get('money_earned', notification_preference.push_money_earned)
        )
    except (DataError, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e
    
    return notification_preference


def update_user_preferences(user_preference: object, data: dict):
    """
    Update user preferences based on the provided data.
    
    Args:
        data (dict): Dictionary containing user preference data.
            It should be in the format:
            {
                "appearance": "light",
            }
    """
    try:
        appearance = data.get('appearance', user_preference.appearance)
        
        user_preference.update(
            appearance=appearance
        )
    except (DataError, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e
    
    return user_preference


def update_security_settings(security_setting: object, data: dict):
    """
    Update Security Settings based on the provided data.
    
    Args:
        data (dict): Dictionary containing user preference data.
            It should be in the format:
            {
                "2fa_method": "email",
                "new_password": "new_password",
            }
    """
    try:
        new_password = data.get('new_password', '')
        two_factor_method = data.get('2fa_method', security_setting.two_factor_method)
        
        if new_password:
            current_user = Trendit3User.query.get(int(get_jwt_identity()))
            hashed_pwd = generate_password_hash(new_password, "pbkdf2:sha256")
            current_user.update(thePassword=hashed_pwd)
        
        # Validate and update security method
        if not SecuritySetting.validate_2fa_method(two_factor_method):
            raise InvalidTwoFactorMethod
        
        security_setting.update(
            two_factor_method=two_factor_method
        )
    except (DataError, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e
    
    return security_setting

