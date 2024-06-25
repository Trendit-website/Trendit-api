from flask_jwt_extended import jwt_required
from . import api
from app.controllers.api import SocialProfileController


@api.route('/users/social-profiles', methods=["GET"])
@jwt_required()
def get_social_profiles():
    return SocialProfileController.get_social_profiles()


@api.route('/users/social-profiles/new', methods=["POST"])
@jwt_required()
def add_social_profile():
    return SocialProfileController.add_social_profile()

@api.route('/users/social-profiles/<platform>', methods=["DELETE"])
@jwt_required()
def delete_social_profile(platform):
    return SocialProfileController.delete_social_profile(platform)


# Deprecated
@api.route('/verified_socials', methods=["GET"])
@jwt_required()
def get_verified_socials():
    return SocialProfileController.get_verified_social_media()

@api.route('/send_social_verification_request', methods=["POST"])
@jwt_required()
def notify_admin():
    return SocialProfileController.send_social_verification_request()

@api.route('/delete-socials/<platform>', methods=["DELETE"])
@jwt_required()
def delete_socials(platform):
    return SocialProfileController.delete_socials(platform)