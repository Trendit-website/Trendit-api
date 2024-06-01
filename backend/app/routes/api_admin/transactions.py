from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin.transactions import TransactionController

@bp.route('/transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_all_transactions():
    return TransactionController.get_all_transactions()


@bp.route('/user_transactions/<str:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_transactions(user_id):
    return TransactionController.get_user_transactions(user_id=user_id)


@bp.route('/user_credit_transactions/<str:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_credit_transactions(user_id):
    return TransactionController.get_user_transactions_by_type(type='credit', user_id=user_id)


@bp.route('/user_debit_transactions/<str:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_debit_transactions(user_id):
    return TransactionController.get_user_transactions_by_type(type='debit', user_id=user_id)


@bp.route('/user_payment_transactions/<str:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_payment_transactions(user_id):
    return TransactionController.get_user_transactions_by_type(type='payment', user_id=user_id)


@bp.route('/user_withdrawal_transactions/<str:user_id>', methods=['POST'])
@roles_required('Junior Admin')
def get_user_withdrawal_transactions(user_id):
    return TransactionController.get_user_transactions_by_type(type='withdrawal', user_id=user_id)