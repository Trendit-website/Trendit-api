from flask_jwt_extended import jwt_required
from app.decorators import roles_required
from app.routes.api_admin import bp
from app.controllers.api_admin import AdminDashboardController
from app.models.role import RoleNames


@bp.route('/dashboard_data', methods=['POST'])
def dashboard_data():
    return AdminDashboardController.admin_dashboard()


@bp.route('/create_junior_admin', methods=['POST'])
def create_junior_admin():
    return AdminDashboardController.create_admin()


@bp.route('/create_admin', methods=['POST'])
def create_admin():
    return AdminDashboardController.create_admin(type=RoleNames.Admin)


@bp.route('/create_super_admin', methods=['POST'])
def create_super_admin():
    return AdminDashboardController.create_admin(type=RoleNames.SUPER_ADMIN)