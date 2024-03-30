from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin.transactions import TransactionController

@bp.route('/transactions', methods=['POST'])
@roles_required('junior_admin')
def get_all_transactions():
    return TransactionController.get_all_tasks()