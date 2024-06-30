from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError, )
from flask_jwt_extended import get_jwt_identity

from config import Config
from ...extensions import db
from ...models import TaskOption, Trendit3User
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception


class TaskOptionsController:
    # ALL TASKS
    @staticmethod
    def get_task_options():
        try:
            user_id = int(get_jwt_identity())

            current_user = Trendit3User.query.filter_by(id=user_id).first()
            if not current_user:
                return error_response("User not found", 404)
            
            user_type = request.args.get('user_type', "advertiser")
            if user_type.lower() not in ['advertiser', 'earner']:
                return error_response("Invalid user type", 400)
            
            task_type = request.args.get('task_type', "advert")
            if task_type.lower() not in ['advert', 'engagement']:
                return error_response("Invalid task type", 400)
            
            task_options = TaskOption.query.filter_by(task_type=task_type).all()
            
            user_wallet = current_user.wallet
            currency_code = user_wallet.currency_code
            
            extra_data = {
                "options": [option.to_dict(user_type, currency_code) for option in task_options]
            }
            
            api_response = success_response("Task options fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            log_exception(f"An unexpected error occurred fetching Task Options", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response