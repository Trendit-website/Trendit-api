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
    return AdminUsersController.get_user_by_id(user_id)


@bp.route('/get_user', methods=['POST'])
@roles_required('Junior Admin')
def get_user_by_email():
    return AdminUsersController.get_user()


@bp.route('/delete-user/<int:user_id>', methods=['DELETE'])
@roles_required('Admin')
def delete_user(user_id):
    return AdminUsersController.delete_user(user_id)


@bp.route('/user_task_metrics/<int:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_task_metrics(user_id):
    return AdminUsersController.get_user_task_metrics(user_id=user_id)


@bp.route('/user_transaction_metrics/<int:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_transaction_metrics(user_id):
    return AdminUsersController.get_user_transaction_metrics(user_id=user_id)