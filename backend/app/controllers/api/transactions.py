import logging
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from ...models.user import Trendit3User
from ...models.payment import Transaction
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log


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
            
            return success_response('Transaction history fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception(f"An exception occurred during fetching transaction history. {str(e)}") # Log the error details for debugging
            return error_response("An error occurred while processing the request", 500)
