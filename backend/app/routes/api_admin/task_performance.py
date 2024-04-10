from flask_jwt_extended import jwt_required

from app.decorators.auth import roles_required
from app.routes.api_admin import bp
from app.controllers.api_admin import AdminTaskPerformanceController


@bp.route('/performed-tasks', methods=['GET'])
@roles_required('Junior Admin')
def get_all_performed_tasks():
    return AdminTaskPerformanceController.get_all_performed_tasks()


@bp.route('/performed-tasks/<int:pt_id>', methods=['GET'])
@roles_required('Junior Admin')
def get_performed_task(pt_id):
    return AdminTaskPerformanceController.get_performed_task(pt_id)


@bp.route('/performed-tasks/<int:pt_id>', methods=['PUT'])
@roles_required('Junior Admin')
def update_performed_task(pt_id):
    return AdminTaskPerformanceController.update_performed_task(pt_id)


@bp.route('/performed-tasks/<int:pt_id>', methods=['DELETE'])
@roles_required('Junior Admin')
def delete_performed_task(pt_id):
    return AdminTaskPerformanceController.delete_performed_task(pt_id)
