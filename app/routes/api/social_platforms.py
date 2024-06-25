from flask_jwt_extended import jwt_required
from . import api
from app.controllers.api import SocialMediaPlatformsController


@api.route('/social-platforms', methods=["GET"])
def get_social_media_platforms():
    return SocialMediaPlatformsController.get_social_media_platforms()