from flask import request
from flask_jwt_extended import jwt_required

from . import api
from ...controllers.api import TaskPerformanceController
from ...decorators import membership_required


@api.route('/generate-task', methods=['POST'])
@jwt_required()
@membership_required()
def generate_task():
    return TaskPerformanceController.generate_task()


@api.route('/perform-task', methods=['POST'])
@jwt_required()
@membership_required()
def perform_task():
    return TaskPerformanceController.perform_task()


@api.route('/performed-tasks', methods=['GET'])
@jwt_required()
def get_current_user_performed_tasks():
    status = request.args.get('status', '')
    
    # Get Performed Tasks by status. (in_review, failed, completed, canceled)
    if status:
        return TaskPerformanceController.get_user_performed_tasks_by_status(status.lower())
    
    return TaskPerformanceController.get_current_user_performed_tasks()



@api.route('/performed-tasks/<pt_id_key>', methods=['GET'])
@jwt_required()
def get_performed_task(pt_id_key):
    return TaskPerformanceController.get_performed_task(pt_id_key)


@api.route('/performed-tasks/<pt_id_key>', methods=['PUT'])
@jwt_required()
def update_performed_task(pt_id_key):
    return TaskPerformanceController.update_performed_task(pt_id_key)


@api.route('/performed-tasks/<pt_id_key>', methods=['DELETE'])
@jwt_required()
def delete_performed_task(pt_id_key):
    return TaskPerformanceController.delete_performed_task(pt_id_key)

@api.route('/performed-tasks/cancel/<pt_id_key>', methods=['PUT'])
@jwt_required()
def cancel_performed_task(pt_id_key):
    return TaskPerformanceController.cancel_performed_task(pt_id_key)



# Get Performed Tasks by their status. (in_review, failed, completed, canceled)
@api.route('/performed-tasks/status/<status>', methods=['GET'])
@jwt_required()
def get_user_performed_tasks_by_status(status):
    return TaskPerformanceController.get_user_performed_tasks_by_status(status.lower())