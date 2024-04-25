from flask_jwt_extended import jwt_required

from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin.transactions import TransactionController

@bp.route('/transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_all_transactions():
    return TransactionController.get_all_transactions()

@bp.route('/user_transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_user_transactions():
    return TransactionController.get_user_transactions()


@bp.route('/user_credit_transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_user_credit_transactions():
    return TransactionController.get_user_transactions_by_type('credit')


@bp.route('/user_debit_transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_user_debit_transactions():
    return TransactionController.get_user_transactions_by_type('debit')


@bp.route('/user_payment_transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_user_payment_transactions():
    return TransactionController.get_user_transactions_by_type('payment')


@bp.route('/user_withdrawal_transactions', methods=['POST'])
@roles_required('Junior Admin')
def get_user_withdrawal_transactions():
    return TransactionController.get_user_transactions_by_type('withdrawal')