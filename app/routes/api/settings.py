'''
This module defines the routes for user setting on the Trendit³ Flask application.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from flask import request
from flask_jwt_extended import jwt_required

from . import api
from ...controllers.api import ManageSettingsController


# get settings
@api.route("settings/notifications", methods=['GET'])
@jwt_required()
def get_notification_settings():
    return ManageSettingsController.get_notification_settings()


@api.route("settings/preferences", methods=['GET'])
@jwt_required()
def get_preference_settings():
    return ManageSettingsController.get_preference_settings()


@api.route("settings/security", methods=['GET'])
@jwt_required()
def get_security_settings():
    return ManageSettingsController.get_security_settings()


# Update settings
@api.route("update-settings", methods=['POST'])
@jwt_required()
def update_settings():
    return ManageSettingsController.update_settings()

@api.route("settings/notifications", methods=['POST'])
@jwt_required()
def update_notification_settings():
    return ManageSettingsController.update_notification_settings()


@api.route("settings/preferences", methods=['POST'])
@jwt_required()
def update_preference_settings():
    return ManageSettingsController.update_preference_settings()


@api.route("settings/security", methods=['POST'])
@jwt_required()
def update_security_settings():
    return ManageSettingsController.update_security_settings()

@api.route("settings/two-fa", methods=['POST'])
@jwt_required()
def update_two_fa_method():
    return ManageSettingsController.update_two_fa_method()

@api.route("settings/password", methods=['POST'])
@jwt_required()
def update_password():
    return ManageSettingsController.update_password()

@api.route("settings/notifications/save", methods=['POST'])
@jwt_required()
def save_notification_settings():
    return ManageSettingsController.save_notification_settings()


@api.route("settings/preferences/save", methods=['POST'])
@jwt_required()
def save_preference_settings():
    return ManageSettingsController.save_preference_settings()


@api.route("settings/security/save", methods=['POST'])
@jwt_required()
def save_security_settings():
    return ManageSettingsController.save_security_settings()


@api.route("settings/activate/google-2fa", methods=['GET'])
@jwt_required()
def activate_google_2fa():
    return ManageSettingsController.activate_google_2fa()

@api.route("settings/activate/complete-google-2fa", methods=['POST'])
@jwt_required()
def complete_google_2fa_activation():
    return ManageSettingsController.complete_google_2fa_activation()

@api.route("settings/deactivate/google-auth-app", methods=['GET'])
@jwt_required()
def deactivate_google_2fa():
    return ManageSettingsController.deactivate_google_2fa()