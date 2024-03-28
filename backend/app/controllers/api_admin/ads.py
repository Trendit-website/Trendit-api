'''
This module defines the controller methods for admin dashboard in the Trendit³ Flask application.

It includes methods for checking username, checking email, signing up, resending email verification code, and logging in.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''

# import logging
# import secrets
# from datetime import timedelta
# from flask import request, current_app
# from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
# from werkzeug.security import generate_password_hash
# from werkzeug.exceptions import UnsupportedMediaType
# from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
# from flask_jwt_extended.exceptions import JWTDecodeError
# from jwt import ExpiredSignatureError, DecodeError
# from sqlalchemy import func

# from ...extensions import db
# from ...models import Role, RoleNames, TempUser, Trendit3User, Address, Profile, OneTimeToken, ReferralHistory, Membership, Wallet, UserSettings, Transaction, TransactionType
# from ...utils.helpers.basic_helpers import console_log, log_exception
# from ...utils.helpers.response_helpers import error_response, success_response
# from ...utils.helpers.location_helpers import get_currency_info
# from ...utils.helpers.auth_helpers import generate_six_digit_code, save_pwd_reset_token, send_2fa_code
# from ...utils.helpers.user_helpers import is_user_exist, get_trendit3_user, referral_code_exists
# from ...utils.helpers.mail_helpers import send_other_emails
