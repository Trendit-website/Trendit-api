from flask import request
from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api import TaskPerformanceController
from app.utils.helpers.basic_helpers import console_log


@bp.route('/generate-task', methods=['GET', 'POST'])
@jwt_required()
def generate_task():
    return TaskPerformanceController.generate_task()



@bp.route('/tasks/initiate/<task_id_key>', methods=['GET'])
@jwt_required()
def initiate_task(task_id_key):
    return TaskPerformanceController.initiate_task(task_id_key)


@bp.route('/perform-task', methods=['POST'])
@jwt_required()
def perform_task():
    return TaskPerformanceController.perform_task()


@bp.route('/performed-tasks', methods=['GET'])
@jwt_required()
def get_current_user_performed_tasks():
    status = request.args.get('status', '')
    
    # Get Performed Tasks by status. (in_review, failed, completed, canceled)
    if status:
        return TaskPerformanceController.get_user_performed_tasks_by_status(status.lower())
    
    return TaskPerformanceController.get_current_user_performed_tasks()



@bp.route('/performed-tasks/<int:pt_id>', methods=['GET'])
@jwt_required()
def get_performed_task(pt_id):
    return TaskPerformanceController.get_performed_task(pt_id)


@bp.route('/performed-tasks/<int:pt_id>', methods=['PUT'])
@jwt_required()
def update_performed_task(pt_id):
    return TaskPerformanceController.update_performed_task(pt_id)


@bp.route('/performed-tasks/<int:pt_id>', methods=['DELETE'])
@jwt_required()
def delete_performed_task(pt_id):
    return TaskPerformanceController.delete_performed_task(pt_id)



# Get Performed Tasks by their status. (in_review, failed, completed, canceled)
@bp.route('/performed-tasks/status/<status>', methods=['GET'])
@jwt_required()
def get_user_performed_tasks_by_status(status):
    return TaskPerformanceController.get_user_performed_tasks_by_status(status.lower())