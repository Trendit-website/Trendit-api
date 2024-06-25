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
        """Get all transactions in the system"""

        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)
            
            transactions = Transaction.query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
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
    def get_user_transactions(user_id=None):
        """Get all transactions for a user"""

        try:
            user_id =int(user_id)
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)
            
            transactions = Transaction.query.filter_by(id=user_id).order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
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
        
    
    @staticmethod
    def get_user_transactions_by_type(type=TransactionType.CREDIT, user_id=None):
        """Get user transactions by type (credit, debit, payment, withdrawal)"""

        try:
            user_id = int(user_id)
            transaction_map = {
                "credit": TransactionType.CREDIT,
                "debit": TransactionType.DEBIT,
                "payment": TransactionType.PAYMENT,
                "withdrawal": TransactionType.WITHDRAWAL
            }
            # transaction_type = data.get('transactionType')
            transaction_type = type
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=20, type=int)
            
            transactions = Transaction.query.filter_by(id=user_id, transaction_type=transaction_map[transaction_type]).order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            transaction_list = [transaction.to_dict() for transaction in transactions.items]
            
            extra_data = {
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': transactions.page,
                'transactions': transaction_list
            }

            return success_response('User transactions fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get user transactions by type:\n", str(e))
            return error_response('Error getting user transactions', 500)


    @staticmethod
    def get_user_balance(user_id=None):
        """Get user's account balance"""

        try:
            user = Trendit3User.query.get(user_id)
            
            if user is None:
                return error_response('User not found', 404)
            
            balance = user.wallet_balance

            extra_data = {'balance': balance}
            return success_response('User balance fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get user balance:\n", str(e))
            return error_response('Error getting user balance', 500)