from flask_jwt_extended import jwt_required
from app.decorators import roles_required
from app.routes.api_admin import bp
from app.controllers.api_admin import AdminAuthController


@bp.route('/admin-login', methods=['POST'])
def admin_login():
    return AdminAuthController.admin_login()


@bp.route('/verify-admin-login', methods=['POST'])
def verify_admin_login():
    # redirect the user to admin page after this
    return AdminAuthController.verify_admin_login()