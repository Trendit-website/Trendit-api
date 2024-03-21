from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.controllers.api_admin import AdminUsersController


@bp.route('/users', methods=['POST'])
@jwt_required()
def get_all_users():
    return AdminUsersController.get_all_users()


@bp.route('/users/<int:user_id>', methods=['POST'])
def get_user(user_id):
    return AdminUsersController.get_user(user_id)
