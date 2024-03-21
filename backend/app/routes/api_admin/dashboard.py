from flask_jwt_extended import jwt_required
from app.decorators import roles_required
from app.routes.api_admin import bp
from app.controllers.api_admin import AdminDashboardController


@bp.route('/dashboard_data', methods=['POST'])
def dashboard_data():
    return AdminDashboardController.admin_dashboard()


@bp.route('/create_admin/<int:user_id>', methods=['POST'])
def create_admin(user_id: int):
    return AdminDashboardController.create_admin()