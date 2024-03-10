import logging
from datetime import timedelta
from flask import request, make_response
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import UnsupportedMediaType
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError, DecodeError

from ...extensions import db
from ...models.role import Role
from ...models.user import TempUser, Trendit3User, Address, Profile, OneTimeToken, ReferralHistory
from ...models.membership import Membership
from ...models.payment import Wallet
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.location_helpers import get_currency_info
from ...utils.helpers.auth_helpers import generate_six_digit_code, send_code_to_email, save_pwd_reset_token
from ...utils.helpers.user_helpers import is_user_exist, get_trendit3_user, referral_code_exists

class SocialAuthController:
    pass