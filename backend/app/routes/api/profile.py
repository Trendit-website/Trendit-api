from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api import ProfileController


@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    return ProfileController.get_profile()

@bp.route('/profile/edit', methods=['POST'])
@jwt_required()
def edit_profile():
    return ProfileController.edit_profile()


@bp.route('/profile/email-edit', methods=['POST'])
@jwt_required()
def user_email_edit():
    return ProfileController.user_email_edit()

@bp.route('/profile/email-verify', methods=['POST'])
@jwt_required()
def verify_email_edit():
    return ProfileController.verify_email_edit()