from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin import AdminTaskController

@bp.route('/tasks', methods=['GET'])
@roles_required('Junior Admin')
def get_all_tasks():
    return AdminTaskController.get_all_tasks()

@bp.route('/failed-tasks', methods=['GET'])
@roles_required('Junior Admin')
def get_all_failed_tasks():
    return AdminTaskController.get_all_failed_tasks()

@bp.route('/approved-tasks', methods=['GET'])
@roles_required('Junior Admin')
def get_all_approved_tasks():
    return AdminTaskController.get_all_approved_tasks()


@bp.route('/pending-tasks', methods=['GET'])
@roles_required('Junior Admin')
def get_all_pending_tasks():
    return AdminTaskController.get_all_pending_tasks()


@bp.route('/tasks/<task_id_key>', methods=['POST'])
@roles_required('Junior Admin')
def get_task(task_id_key):
    return AdminTaskController.get_task(task_id_key)


@bp.route('/tasks/approve/<task_id_key>', methods=['POST'])
@roles_required('Junior Admin')
def approve_task(task_id_key):
    return AdminTaskController.approve_task(task_id_key)


@bp.route('/tasks/reject/<task_id_key>', methods=['POST'])
@roles_required('Junior Admin')
def reject_task(task_id_key):
    return AdminTaskController.reject_task(task_id_key)


@bp.route('/tasks/<task_id_key>/performances', methods=['POST'])
@roles_required('Junior Admin')
def get_task_performances(task_id_key):
    return AdminTaskController.get_task_performances(task_id_key)


@bp.route('/tasks/verify-performance', methods=['POST'])
@roles_required('Junior Admin')
def verify_task_performance():
    return AdminTaskController.verify_performed_task()