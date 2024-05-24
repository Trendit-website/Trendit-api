'''
This module defines the routes for authentication operations in the Trendit³ Flask application.

It includes routes for signing up, verifying email, logging in, verifying 2FA, forgetting password, and resetting password.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask import request
from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api import AuthController, ProfileController


# REGISTRATION ENDPOINTS
@api.route("/signup", methods=['POST'])
def signUp():
    return AuthController.signUp()

@api.route("/verify-email", methods=['POST'])
def verify_email():
    return AuthController.verify_email()

@api.route("/complete-registration", methods=['POST'])
def complete_registration():
    return AuthController.complete_registration()

# AUTHENTICATION ENDPOINTS
@api.route("/login", methods=['POST'])
def login():
    return AuthController.login()

@api.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    return AuthController.verify_2fa()


@api.route("/forgot-password", methods=['POST'])
def forgot_password():
    return AuthController.forgot_password()

@api.route("/reset-password", methods=['POST'])
def reset_password():
    return AuthController.reset_password()


@api.route("/resend-code", methods=['POST'])
def resend_code():
    code_type = request.args.get('code_type', 'email-signup')
    
    if code_type == 'email-signup':
        return AuthController.resend_email_verification_code()
    if code_type == 'email-edit':
        return ProfileController.user_email_edit()
    if code_type == 'pwd-reset':
        return AuthController.forgot_password()
    if code_type == 'two-fa':
        return AuthController.resend_two_fa()

@api.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    return AuthController.logout()

@api.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    return AuthController.delete_account()


@api.route('/check-username', methods=['POST'])
def username_check():
    return AuthController.username_check()

@api.route('/check-email', methods=['POST'])
def email_check():
    return AuthController.email_check()

@api.route('/user/type', methods=['GET'])
def update_user_role():
    return AuthController.update_user_role()