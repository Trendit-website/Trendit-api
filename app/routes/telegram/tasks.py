from . import telegram_bp
from ...controllers.telegram import TasksTelegramController
from ...decorators import roles_required


@telegram_bp.route('/pending-tasks', methods=["GET"])
@roles_required("Super Admin", "Admin", "Junior Admin")
def get_pending_tasks():
    return TasksTelegramController.get_pending_tasks()

