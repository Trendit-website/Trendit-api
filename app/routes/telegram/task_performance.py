from . import telegram_bp
from ...controllers.telegram import TaskPerformanceTelegramController
from ...decorators import roles_required


@telegram_bp.route('/performed-tasks/<int:pt_id>', methods=['GET'])
@roles_required("Super Admin", "Admin", "Junior Admin")
def get_performed_task(pt_id):
    return TaskPerformanceTelegramController.get_performed_task(pt_id)