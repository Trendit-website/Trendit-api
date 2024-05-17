from flask_jwt_extended import jwt_required
from flask import request
from . import api
from app.controllers.api import SocialVerificationController


@api.route('/verified_socials', method=["POST"])
@jwt_required()
def get_verified_socials():
    return SocialVerificationController.get_verified_social_media()