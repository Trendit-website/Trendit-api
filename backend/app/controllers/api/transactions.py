import logging
from flask import request
from flask_jwt_extended import get_jwt_identity

from ...models import Trendit3User, Payment, Transaction
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.payment_helpers import get_total_amount_earned, get_total_amount_spent


class TransactionController:
    @staticmethod
    def get_transaction_history():
        """
        Fetches the transaction history for a user.

        This function extracts the current_user_id from the jwt identity, checks if the user exists, and if so, fetches the user's payment history from the database and returns it. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the request, a status code, a message (and payment history in case of success), and an HTTP status code.
        """
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            per_page = 15
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            # Fetch payment records from the database
            pagination = Transaction.query.filter_by(trendit3_user_id=current_user_id) \
                .order_by(Transaction.created_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            transactions = pagination.items
            current_transactions = [transaction.to_dict() for transaction in transactions]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "transactions_history": current_transactions,
            }
            
            if not transactions:
                return success_response(f'No transactions has been made', 200, extra_data)
            
            api_response = success_response('Transaction history fetched successfully', 200, extra_data)
        except Exception as e:
            log_exception(f"An exception occurred fetching transaction history", e)
            api_response = error_response("An error occurred while processing the request", 500)
        
        return api_response

    
    @staticmethod
    def get_transaction_stats():
        try:
            # get the current user's ID
            current_user_id = get_jwt_identity()
            
            # Check if user exists
            current_user = Trendit3User.query.get(current_user_id)
            if current_user is None:
                return error_response('User not found', 404)
            
            # get the user's wallet balance
            wallet_balance = current_user.wallet_balance
            
            
            # get the total earnings for the current month and overall
            total_earned_overall, total_earned_current_month = get_total_amount_earned(current_user_id)
            
            # get the total amount spent for the current month and overall
            total_spent_overall, total_spent_current_month = get_total_amount_spent(current_user_id)
            
            
            # create a dictionary with the stats
            metrics = {
                'wallet_balance': wallet_balance,
                'total_earned_overall': total_earned_overall,
                'total_earned_current_month': total_earned_current_month,
                'total_spent_overall': total_spent_overall,
                'total_spent_current_month': total_spent_current_month,
                'currency_code': current_user.wallet.currency_code,
                'currency_name': current_user.wallet.currency_name
            }
            
            api_response = success_response(f"metrics fetched successfully", 200, {"metrics": metrics})
        except Exception as e:
            log_exception(f"An exception occurred fetching transaction metrics.", e)
            api_response = error_response(f"Error fetching transaction metrics: {str(e)}", 500)
        
        return api_response
    