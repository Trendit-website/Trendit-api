from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.controllers.api_admin import AdminTaskController

@bp.route('/tasks', methods=['POST'])
def get_all_tasks():
    return AdminTaskController.get_all_tasks()


@bp.route('/tasks/<int:task_id>', methods=['POST'])
def get_task(task_id):
    return AdminTaskController.get_task(task_id)


@bp.route('/approve-task/<int:task_id>', methods=['POST'])
def approve_task(task_id):
    return AdminTaskController.approve_task(task_id)


@bp.route('/reject-task/<int:task_id>', methods=['POST'])
def reject_task(task_id):
    return AdminTaskController.reject_task(task_id)