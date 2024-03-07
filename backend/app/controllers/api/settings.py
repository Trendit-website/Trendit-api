'''
This module defines the controller methods for user setting on the Trendit³ Flask application.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

import logging
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...models import Trendit3User, UserSettings, NotificationPreference, UserPreference, SecuritySetting
from ...exceptions import InvalidTwoFactorMethod
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.settings_helpers import update_notification_preferences, update_user_preferences, update_security_settings


class ManageSettingsController:
    @staticmethod
    def get_notification_settings():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            user_settings = UserSettings.query.filter_by(trendit3_user_id=current_user_id).first()
            if not user_settings:
                user_settings = UserSettings(trendit3_user_id=current_user_id)
                db.session.add(user_settings)
            
            
            if not user_settings.notification_preference:
                user_settings.notification_preference = NotificationPreference()
            
            db.session.commit()
            
            notification_preference = user_settings.notification_preference
            
            extra_data = {"notification_preference": notification_preference.to_dict()}
            
            api_response = success_response('Notification preferences fetched successfully', 200, extra_data)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred fetching preference', e)
            return error_response('Error interacting with the database.', 500)
        except Exception as e:
            db.session.rollback()
            msg = f'An unexpected error occurred fetching notification preference: {e}'
            logging.exception(f"An exception occurred fetching notification preference. {str(e)}")
            api_response = error_response(msg, 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def get_preference_settings():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            
            user_settings = UserSettings.query.filter_by(trendit3_user_id=current_user_id).first()
            if not user_settings:
                user_settings = UserSettings(trendit3_user_id=current_user_id)
                db.session.add(user_settings)
            
            if not user_settings.user_preference:
                user_settings.user_preference = UserPreference()
            
            user_preference = user_settings.user_preference
            
            db.session.commit()
            
            extra_data = {"user_preferences": user_preference.to_dict()}
            
            api_response = success_response('preferences fetched successfully', 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred fetching preference', e)
            api_response = error_response('Error interacting with the database.', 500)
        except Exception as e:
            db.session.rollback()
            msg = f'An unexpected error occurred fetching user preference: {e}'
            logging.exception(f"An exception occurred fetching user preference. {str(e)}")
            api_response = error_response(msg, 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def get_security_settings():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            
            user_settings = UserSettings.query.filter_by(trendit3_user_id=current_user_id).first()
            if not user_settings:
                user_settings = UserSettings(trendit3_user_id=current_user_id)
                db.session.add(user_settings)
            
            if not user_settings.security_setting:
                user_settings.security_setting = SecuritySetting()
            
            db.session.commit()
            
            security_setting = user_settings.security_setting
            
            extra_data = {"security_settings": security_setting.to_dict()}
            
            api_response = success_response('Security settings fetched successfully', 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred fetching security settings', e)
            api_response = error_response('Error interacting with the database.', 500)
        except Exception as e:
            db.session.rollback()
            msg = f'An unexpected error occurred fetching security settings: {e}'
            log_exception(f"An exception occurred fetching security settings.", str(e))
            api_response = error_response(msg, 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def update_notification_settings():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            data = request.get_json()
            
            user_settings = UserSettings.query.filter_by(trendit3_user_id=current_user_id).first()
            if not user_settings:
                user_settings = UserSettings(trendit3_user_id=current_user_id)
                db.session.add(user_settings)
            
            
            if not user_settings.notification_preference:
                user_settings.notification_preference = NotificationPreference()
            
            notification_preference = user_settings.notification_preference
            
            # Update notification preferences
            notification_preferences = update_notification_preferences(notification_preference, data)
            
            extra_data = {"notification_preference": notification_preferences.to_dict()}
            
            db.session.commit()
            api_response = success_response('Notification preferences updated successfully', 200, extra_data)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred saving preference', e)
            return error_response('Error interacting with the database.', 500)
        except Exception as e:
            db.session.rollback()
            msg = f'An unexpected error occurred saving notification preference: {e}'
            logging.exception(f"An exception occurred saving notification preference. {str(e)}")
            api_response = error_response(msg, 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def update_preference_settings():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            data = request.get_json()
            
            user_settings = UserSettings.query.filter_by(trendit3_user_id=current_user_id).first()
            if not user_settings:
                user_settings = UserSettings(trendit3_user_id=current_user_id)
                db.session.add(user_settings)
            
            if not user_settings.user_preference:
                user_settings.user_preference = UserPreference()
            
            user_preference = user_settings.user_preference
            
            # Update user preferences
            user_preferences = update_user_preferences(user_preference, data)
            
            extra_data = {"user_preferences": user_preferences.to_dict()}
            
            db.session.commit()
            api_response = success_response('preferences updated successfully', 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred saving preference', e)
            api_response = error_response('Error interacting with the database.', 500)
        except Exception as e:
            db.session.rollback()
            msg = f'An unexpected error occurred saving user preference: {e}'
            logging.exception(f"An exception occurred saving user preference. {str(e)}")
            api_response = error_response(msg, 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def update_security_settings():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            data = request.get_json()
            
            user_settings = UserSettings.query.filter_by(trendit3_user_id=current_user_id).first()
            if not user_settings:
                user_settings = UserSettings(trendit3_user_id=current_user_id)
                db.session.add(user_settings)
            
            if not user_settings.security_setting:
                user_settings.security_setting = SecuritySetting()
            
            security_setting = user_settings.security_setting
            
            # Update user preferences
            security_settings = update_security_settings(security_setting, data)
            
            extra_data = {"security_settings": security_settings.to_dict()}
            
            db.session.commit()
            api_response = success_response('Security settings updated successfully', 200, extra_data)
        except InvalidTwoFactorMethod as e:
            db.session.rollback()
            api_response = error_response(f'{e}', 400)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred saving security settings', e)
            api_response = error_response('Error interacting with the database.', 500)
        except Exception as e:
            db.session.rollback()
            msg = f'An unexpected error occurred saving security settings: {e}'
            logging.exception(f"An exception occurred saving security settings. {str(e)}")
            api_response = error_response(msg, 500)
        finally:
            db.session.close()
        
        return api_response

