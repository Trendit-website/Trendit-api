import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.models.payment import Transaction, TransactionType
from app.models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails


class TransactionController:

    @staticmethod
    def get_all_transactions():
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)
            
            transactions = Transaction.query.paginate(page=page, per_page=per_page, error_out=False)
            transaction_list = [transaction.to_dict() for transaction in transactions.items]
            
            extra_data = {
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': transactions.page,
                'transactions': transaction_list
            }

            return success_response('All transactions fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get all transactions:\n", str(e))
            return error_response('Error getting all tasks', 500)

        
    @staticmethod
    def get_user_transactions():
        try:
            data = request.get_json()
            user_id = data.get('userId')
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)
            
            transactions = Transaction.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
            transaction_list = [transaction.to_dict() for transaction in transactions.items]
            
            extra_data = {
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': transactions.page,
            'transactions': transaction_list
            }

            return success_response('User transactions fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get user transactions:\n", str(e))
            return error_response('Error getting user transactions', 500)
