import logging
from datetime import timedelta
from flask import request, make_response
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import UnsupportedMediaType
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError, DecodeError
from flask import redirect, request, session, jsonify
from requests_oauthlib import OAuth2Session
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
import requests
import random
import os

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



# Facebook OAuth configuration
CLIENT_ID = os.environ.get('FB_CLIENT_ID')
CLIENT_SECRET = os.environ.get('FB_CLIENT_SECRET')
FB_REDIRECT_URI = os.environ.get('FB_REDIRECT_URI')

# Facebook OAuth endpoints
FB_AUTHORIZATION_BASE_URL = os.environ.get('FB_AUTHORIZATION_BASE_URL')
TOKEN_URL = os.environ.get('FB_TOKEN_URL')


# Google OAuth configuration
GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
# REDIRECT_URI = 'http://localhost:5000/callback'  # Set this to your callback URL
GOOGLE_REDIRECT_URI = 'https://api.trendit3.com/google/callback'

# Google OAuth endpoints
GOOGLE_AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'


class SocialAuthController:

    @staticmethod
    def fb_signup():

        try:
            facebook = OAuth2Session(CLIENT_ID, redirect_uri=FB_REDIRECT_URI)
            facebook = facebook_compliance_fix(facebook)
            authorization_url, state = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

            # Save the state to compare it in the callback
            session['oauth_state'] = state

            return redirect(authorization_url)
        
        except Exception as e:
            msg = f'An error occurred while logging in through facebook: {e}'
            logging.exception("An error occured while logging in through facebook ")
            status_code = 500
            return error_response(msg, status_code)
        
    @staticmethod
    def fb_signup_callback():
        # Check for CSRF attacks
        # if request.args.get('state') != session.pop('oauth_state', None):
        #     print('here')
        #     return 'Invalid state'
        try:
            facebook = OAuth2Session(CLIENT_ID, redirect_uri=FB_REDIRECT_URI)
            token = facebook.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)


            # Use the token to make a request to the Facebook Graph API to get user data
            graph_api_url = 'https://graph.facebook.com/me'
            params = {'access_token': token['access_token'], 'fields': 'id,name,email'}
            response = requests.get(graph_api_url, params=params)

            if response.status_code == 200:
                user_data = response.json()
                extra_data = {"user_data": user_data}
                # change this to actually log in the user
                return success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while fetching user data from facebook: {e}'
            logging.exception("An error occured while fetching user data from facebook ")
            status_code = 500
            return error_response(msg, status_code)


    @staticmethod
    def fb_login():

        try:
            facebook = OAuth2Session(CLIENT_ID, redirect_uri=FB_REDIRECT_URI)
            facebook = facebook_compliance_fix(facebook)
            authorization_url, state = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

            # Save the state to compare it in the callback
            session['oauth_state'] = state

            return redirect(authorization_url)
        
        except Exception as e:
            msg = f'An error occurred while logging in through facebook: {e}'
            logging.exception("An error occured while logging in through facebook ")
            status_code = 500
            return error_response(msg, status_code)
        
    @staticmethod
    def fb_login_callback():
        # Check for CSRF attacks
        # if request.args.get('state') != session.pop('oauth_state', None):
        #     print('here')
        #     return 'Invalid state'
        try:
            facebook = OAuth2Session(CLIENT_ID, redirect_uri=FB_REDIRECT_URI)
            token = facebook.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=request.url)


            # Use the token to make a request to the Facebook Graph API to get user data
            graph_api_url = 'https://graph.facebook.com/me'
            params = {'access_token': token['access_token'], 'fields': 'id,name,email'}
            response = requests.get(graph_api_url, params=params)

            if response.status_code == 200:
                user_data = response.json()
                extra_data = {"user_data": user_data}
                # change this to actually log in the user
                return success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while fetching user data from facebook: {e}'
            logging.exception("An error occured while fetching user data from facebook ")
            status_code = 500
            return error_response(msg, status_code)


    @staticmethod
    def tiktok_signup():

        try:
            csrf_state = str(random.random())[2:]
            response = make_response()
            response.set_cookie('csrfState', csrf_state, max_age=60000)

            url = 'https://www.tiktok.com/v2/auth/authorize/'

            # the following params need to be in `application/x-www-form-urlencoded` format.
            url += '?client_key={}'.format(os.environ.get('TIKTOK_CLIENT_KEY'))
            url += '&scope=user.info.basic'
            url += '&response_type=code'
            url += '&redirect_uri={}'.format(request.url_root[:-1] + '/tt_callback') # figure out how to get the redirect uri
            url += '&state=' + csrf_state

            return redirect(url)
        
        except Exception as e:
            msg = f'An error occurred while logging in through tiktok: {e}'
            logging.exception("An error occured while logging in through tiktok ")
            status_code = 500
            return error_response(msg, status_code)

    @staticmethod
    def tiktok_signup_callback():

        try:
            user_data = request.get_json()
            # code = data.get('code')
            # scope = data.get('scope')
            # state = data.get('state')
            # error = data.get('error')
            extra_data = {"user_data": user_data}
            # change this to actually log in the user
            return success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while fetching user data from tiktok: {e}'
            logging.exception("An error occured while fetching user data from tiktok ")
            status_code = 500
            return error_response(msg, status_code)


    @staticmethod
    def tiktok_login():

        try:
            csrf_state = str(random.random())[2:]
            response = make_response()
            response.set_cookie('csrfState', csrf_state, max_age=60000)

            url = 'https://www.tiktok.com/v2/auth/authorize/'

            # the following params need to be in `application/x-www-form-urlencoded` format.
            url += '?client_key={}'.format(os.environ.get('TIKTOK_CLIENT_KEY'))
            url += '&scope=user.info.basic'
            url += '&response_type=code'
            url += '&redirect_uri={}'.format(request.url_root[:-1] + '/tt_callback') # figure out how to get the redirect uri
            url += '&state=' + csrf_state

            return redirect(url)
        
        except Exception as e:
            msg = f'An error occurred while logging in through tiktok: {e}'
            logging.exception("An error occured while logging in through tiktok ")
            status_code = 500
            return error_response(msg, status_code)

    @staticmethod
    def tiktok_login_callback():

        try:
            user_data = request.get_json()
            # code = data.get('code')
            # scope = data.get('scope')
            # state = data.get('state')
            # error = data.get('error')
            extra_data = {"user_data": user_data}
            # change this to actually log in the user
            return success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while fetching user data from tiktok: {e}'
            logging.exception("An error occured while fetching user data from tiktok ")
            status_code = 500
            return error_response(msg, status_code)

    
    @staticmethod
    def google_login():
        google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=GOOGLE_REDIRECT_URI, scope=['profile', 'email'])
        authorization_url, state = google.authorization_url(GOOGLE_AUTHORIZATION_BASE_URL, access_type='offline') # offline for refresh token

        # Save the state to compare it in the callback
        session['oauth_state'] = state

        return redirect(authorization_url)

    @staticmethod
    def google_login_callback():
        # Check for CSRF attacks
        # if request.args.get('state') != session.pop('oauth_state', None):
        #     return 'Invalid state'

        google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=GOOGLE_REDIRECT_URI)
        token = google.fetch_token(GOOGLE_TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url)

        # Use the token to make a request to the Google API to get user data
        response = google.get(GOOGLE_USER_INFO_URL)

        if response.status_code == 200:
            user_data = response.json()
            # Return the user's data (you can customize this response as needed)
            return jsonify(user_data), 200
        else:
            return 'Failed to fetch user data from Google API'
