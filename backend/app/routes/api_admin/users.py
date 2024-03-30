from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin import AdminUsersController


@bp.route('/users', methods=['POST'])
@roles_required('Junior Admin')
def get_all_users():
    return AdminUsersController.get_all_users()


@bp.route('/user/<int:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user(user_id):
    return AdminUsersController.get_user(user_id)
