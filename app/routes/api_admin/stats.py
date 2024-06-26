
from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin.stats import AdminStatsController

@bp.route('/stats', methods=["GET"])
@roles_required('Admin')
def get_statistics():
    return AdminStatsController.get_statistics()

