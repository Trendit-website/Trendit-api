'''
This module defines the controller methods for authentication operations in the Trendit³ Flask application.

It includes methods for checking username, checking email, signing up, resending email verification code, and logging in.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''

import logging
import secrets
from datetime import timedelta
from flask import request, current_app
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import UnsupportedMediaType
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError, DecodeError

from ...extensions import db
from ...models import Role, TempUser, Trendit3User, Address, Profile, OneTimeToken, ReferralHistory, Membership, Wallet, UserSettings
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.location_helpers import get_currency_info
from ...utils.helpers.auth_helpers import generate_six_digit_code, send_code_to_email, save_pwd_reset_token, send_2fa_code
from ...utils.helpers.user_helpers import is_user_exist, get_trendit3_user, referral_code_exists

class AdminAuthController:

    @staticmethod
    def admin_login():
        """
        This function takes in email and if the user exists and has the required roles,
        sends a login link to their email
        """
        try:
            data = request.get_json()
            email = data.get('email')
            required_roles = ['Admin', 'Moderator']

            user = get_trendit3_user(email)

            if not user:
                return error_response('Email is incorrect or doesn\'t exist', 401)
            
            if user and any(role.name in required_roles for role in user.roles):
                token = secrets.token_urlsafe(16)
                signin_token = OneTimeToken.query.filter(OneTimeToken.trendit3_user_id == user.id).first()
                if signin_token:
                    signin_token.update(token=token, used=False)
                    send_code_to_email(email, token)
                    return success_response('Login link sent to email', 200)
                else:
                    new_signin_token = OneTimeToken.create_token(token=token, trendit3_user_id=user.id)
                    send_code_to_email(email, token)
                    return success_response('Login link sent to email', 200)
                
            else:
                return error_response('You do not have the required roles to access this resource', 403)
                
        except Exception as e:
            console_log('Admin Login EXCEPTION', str(e))
            current_app.logger.error(f"An error occurred saving the Admin Login token in the database: {str(e)}")
            db.session.rollback()
            db.session.close()
            return None


    @staticmethod
    def verify_admin_login(token):
        """
        This function takes in the token sent to the user's email and verifies it
        """
        try:
            signin_token = OneTimeToken.query.filter(OneTimeToken.token == token).first()
            if signin_token and not signin_token.used:
                signin_token.update(used=True)
                access_token = create_access_token(identity=signin_token.trendit3_user_id, expires_delta=timedelta(minutes=1440), additional_claims={'type': 'access'})
                extra_data = {'access_token':access_token}
                return success_response('Login successful', 200, extra_data)
            else:
                return error_response('Token is invalid or has been used', 401)
        except Exception as e:
            console_log('Admin Login Verification EXCEPTION', str(e))
            current_app.logger.error(f"An error occurred verifying the Admin Login token in the database: {str(e)}")
            db.session.rollback()
            return None
        
        finally:
            db.session.close()