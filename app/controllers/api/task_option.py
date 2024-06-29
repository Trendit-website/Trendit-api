from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError, )

from config import Config
from ...extensions import db
from ...models import TaskOption, Task, AdvertTask, EngagementTask, TaskPaymentStatus, TaskStatus, TaskPerformance, Trendit3User
from ...utils.helpers.task_helpers import save_task, get_tasks_dict_grouped_by_field, fetch_task, get_aggregated_task_counts_by_field, fetch_performed_task
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception


class TaskOptionsController:
    # ALL TASKS
    @staticmethod
    def get_task_options():
        try:
            task_type = request.args.get('type')
            
            if task_type.lower() not in ['advert', 'engagement']:
                return error_response("Invalid task type", 400)
            
            task_options = TaskOption.query.filter_by(task_type=task_type).all()
            
            extra_data = {
                "options": [{ 
                    'name': option.name, 
                    'description': option.description, 
                    'price': option.price 
                } for option in task_options]
            }
            
            api_response = success_response("Task options fetched successfully", 200, extra_data)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred fetching Task Options", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response