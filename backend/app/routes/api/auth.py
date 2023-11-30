from flask import request
from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api import AuthController, ProfileController

@bp.route("/signup", methods=['POST'])
def signUp():
    return AuthController.signUp()

@bp.route("/verify-email", methods=['POST'])
def verify_email():
    return AuthController.verify_email()

@bp.route("/login", methods=['POST'])
def login():
    return AuthController.login()

@bp.route("/forgot-password", methods=['POST'])
def forgot_password():
    return AuthController.forgot_password()

@bp.route("/reset-password", methods=['POST'])
def reset_password():
    return AuthController.reset_password()

@bp.route("/resend-code", methods=['POST'])
def resend_code():
    code_type = request.args.get('code_type', 'email-signup')
    
    if code_type == 'email-signup':
        return AuthController.resend_email_verification_code()
    if code_type == 'email-edit':
        return ProfileController.user_email_edit()
    if code_type == 'pwd-reset':
        return AuthController.forgot_password()

@bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    return AuthController.logout()