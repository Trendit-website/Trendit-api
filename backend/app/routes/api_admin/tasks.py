from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin import AdminTaskController

@bp.route('/tasks', methods=['POST'])
@roles_required('Junior Admin')
def get_all_tasks():
    return AdminTaskController.get_all_tasks()

@bp.route('/failed-tasks', methods=['POST'])
@roles_required('Junior Admin')
def get_all_failed_tasks():
    return AdminTaskController.get_all_failed_tasks()

@bp.route('/approved-tasks', methods=['POST'])
@roles_required('Junior Admin')
def get_all_approved_tasks():
    return AdminTaskController.get_all_approved_tasks()


@bp.route('/pending-tasks', methods=['POST'])
@roles_required('Junior Admin')
def get_all_pending_tasks():
    return AdminTaskController.get_all_pending_tasks()


@bp.route('/tasks/<int:task_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_task(task_id):
    return AdminTaskController.get_task(task_id)


@bp.route('/approve-task/<int:task_id>', methods=['POST'])
@roles_required('Junior Admin')
def approve_task(task_id):
    return AdminTaskController.approve_task(task_id)


@bp.route('/reject-task/<int:task_id>', methods=['POST'])
@roles_required('Junior Admin')
def reject_task(task_id):
    return AdminTaskController.reject_task(task_id)