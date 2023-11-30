from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.controllers.api_admin import AdminTaskPerformanceController


@bp.route('/performed-tasks', methods=['GET'])
@jwt_required()
def get_all_performed_tasks():
    return AdminTaskPerformanceController.get_all_performed_tasks()


@bp.route('/performed-tasks/<int:pt_id>', methods=['GET'])
@jwt_required()
def get_performed_task(pt_id):
    return AdminTaskPerformanceController.get_performed_task(pt_id)


@bp.route('/performed-tasks/<int:pt_id>', methods=['PUT'])
@jwt_required()
def update_performed_task(pt_id):
    return AdminTaskPerformanceController.update_performed_task(pt_id)


@bp.route('/performed-tasks/<int:pt_id>', methods=['DELETE'])
@jwt_required()
def delete_performed_task(pt_id):
    return AdminTaskPerformanceController.delete_performed_task(pt_id)
