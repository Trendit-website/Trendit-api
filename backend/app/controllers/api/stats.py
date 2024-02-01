import logging
from datetime import datetime
from flask import request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func

from ...extensions import db
from config import Config
from ...models.user import Trendit3User
from ...models.task import Task, AdvertTask, EngagementTask, TaskPerformance
from ...models.item import Item
from ...models.payment import Payment
from ...utils.helpers.response_helpers import success_response, error_response


class StatsController():
    @staticmethod
    def get_stats():
        error = False
        try:
            # get the current user's ID
            current_user_id = get_jwt_identity()
            
            # get the user's wallet balance
            wallet_balance = Trendit3User.query.filter_by(id=current_user_id).first().wallet_balance
            
            # get the total task performed
            total_task_done = TaskPerformance.query.filter_by(status='completed').count()
            
            # TODO: get the total number of product/services sold
            # total_items_sold = Item.query.filter_by(sold=True).count() or 0
            
            # TODO: get the total amount spent
            total_amount_spent = db.session.query(func.sum(Payment.amount)).filter_by(trendit3_user_id=current_user_id).scalar()
            
            # TODO: get the total earnings for the current month
            '''
            today = datetime.today()
            start_of_month = datetime(today.year, today.month, 1)
            total_earnings = Task.query.filter_by(trendit3_user_id=current_user_id, sold=True).filter(Task.date_sold >= start_of_month).sum('price') or 0
            '''
            
            # create a dictionary with the stats
            stats = {
                'wallet_balance': wallet_balance,
                #'total_earnings': total_earnings,
                'total_task_done': total_task_done,
                'total_amount_spent': total_amount_spent,
            }
            msg = f"stats fetched successfully"
            status_code = 200
        except Exception as e:
            error = True
            status_code = 500
            msg = f"Error fetching stats: {str(e)}"
            logging.exception(f"An exception occurred fetching stats.\n {str(e)}")
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, {"stats": stats})