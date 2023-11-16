from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api import TaskPerformanceController


@bp.route('/perform-task', methods=['POST'])
@jwt_required()
def perform_task():
    return TaskPerformanceController.perform_task()


@bp.route('/performed-tasks', methods=['GET'])
@jwt_required()
def get_all_performed_tasks():
    return TaskPerformanceController.get_all_performed_tasks()


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
