import logging
from flask_jwt_extended import get_jwt_identity

from ...models import Trendit3User, TaskPerformance, Item
from ...utils.helpers.response_helpers import success_response, error_response


class StatsController():
    @staticmethod
    def get_stats():
        try:
            # get the current user's ID
            current_user_id = get_jwt_identity()
            
            # get the user's wallet balance
            wallet_balance = Trendit3User.query.filter_by(id=current_user_id).first().wallet_balance
            
            # get the total task performed
            total_task_done = TaskPerformance.query.filter_by(status='completed').count()
            
            # TODO: get the total number of product/services sold
            # total_items_sold = Item.query.filter_by(sold=True).count() or 0
            
            # create a dictionary with the stats
            metrics = {
                'wallet_balance': wallet_balance,
                'total_task_done': total_task_done,
            }
            msg = f"stats fetched successfully"
            api_response = success_response(f"metrics fetched successfully", 200, {"metrics": metrics})
        except Exception as e:
            logging.exception(f"An exception occurred fetching metrics.\n {str(e)}")
            api_response = error_response(f"Error fetching metrics: {str(e)}", 500)
        
        return api_response