'''
This module defines the routes for social authentication operations in the Trendit³ Flask application.

It includes routes for signing up with google, facebook and tiktok accounts.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''
from flask import current_app
from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api import SocialAuthController
from ...utils.helpers.mail_helpers import send_async_other_email
from ...utils.helpers.response_helpers import success_response


@api.route('/facebook_signup', methods=["GET"])
def fb_signup():
    return SocialAuthController.fb_signup()


@api.route('/fb_signup_callback', methods=["GET"])
def fb_signup_callback():
    return SocialAuthController.fb_signup_callback()


@api.route('/facebook_login', methods=["GET"])
def fb_login():
    return SocialAuthController.fb_login()


@api.route('/fb_login_callback', methods=["GET"])
def fb_callback():
    return SocialAuthController.fb_login_callback()


@api.route('/tt_login', methods=["GET"])
def tt_login():
    return SocialAuthController.tiktok_login()


@api.route('/tt_login_callback', methods=["GET"])
def tt_login_callback():
    return SocialAuthController.tiktok_login_callback()


@api.route('/tt_signup', methods=["GET"])
def tt_signup():
    return SocialAuthController.tiktok_login()


@api.route('/tt_signup_callback', methods=["GET"])
def tt_signup_callback():
    return SocialAuthController.tiktok_signup_callback()


@api.route('/gg_login', methods=["GET"])
def gg_login():
    return SocialAuthController.google_login()


@api.route('/gg_login_callback', methods=["GET"])
def gg_login_callback():
    return SocialAuthController.google_login_callback()


@api.route('/gg_signup', methods=["GET"])
def gg_signup():
    return SocialAuthController.google_signup()


@api.route('/gg_signup_callback', methods=["GET"])
def gg_signup_callback():
    return SocialAuthController.google_signup_callback()


@api.route('/welcome_email', methods=["GET"])
def welcome():
    send_async_other_email(current_app._get_current_object(), user_email='chrisdev0000@gmail.com', email_type='welcome')
    return success_response('email sent', 200)


@api.route('/app/gg_login', methods=["GET"])
def gg_login_app():
    return SocialAuthController.google_login_app()


@api.route('/app/gg_login_callback', methods=["GET"])
def gg_login_callback_app():
    return SocialAuthController.google_login_callback_app()


@api.route('/app/gg_signup', methods=["GET"])
def gg_signup_app():
    return SocialAuthController.google_signup_app()


@api.route('/app/gg_signup_callback', methods=["GET"])
def gg_signup_callback_app():
    return SocialAuthController.google_signup_callback_app()