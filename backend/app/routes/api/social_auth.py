'''
This module defines the routes for social authentication operations in the Trendit³ Flask application.

It includes routes for signing up with google, facebook and tiktok accounts.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''
from flask import request
from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api import SocialAuthController


@api.route('/facebook_signup')
def fb_signup():
    return SocialAuthController.fb_signup()


@api.route('/fb_signup_callback')
def fb_signup_callback():
    return SocialAuthController.fb_signup_callback()

@api.route('/facebook_login')
def fb_login():
    return SocialAuthController.fb_login()


@api.route('/fb_login_callback')
def fb_callback():
    return SocialAuthController.fb_login_callback()


@api.route('/tt_login')
def tt_login():
    return SocialAuthController.tiktok_login()


@api.route('/tt_login_callback')
def tt_login_callback():
    return SocialAuthController.tiktok_login_callback()


@api.route('/tt_signup')
def tt_signup():
    return SocialAuthController.tiktok_login()


@api.route('/tt_signup_callback')
def tt_signup_callback():
    return SocialAuthController.tiktok_signup_callback()