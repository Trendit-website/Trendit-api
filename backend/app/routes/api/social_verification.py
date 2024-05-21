from flask_jwt_extended import jwt_required
from flask import request
from . import api
from app.controllers.api import SocialVerificationController
from app.controllers.api import NotificationController


@api.route('/verified_socials', methods=["POST"])
@jwt_required()
def get_verified_socials():
    return SocialVerificationController.get_verified_social_media()


@api.route('/send_social_verification_request', methods=["POST"])
@jwt_required()
def notify_admin():
    return NotificationController.send_social_verification_request()