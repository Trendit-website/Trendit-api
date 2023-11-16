import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.models.task import Task, AdvertTask, EngagementTask, TaskPerformance
from app.models.payment import Wallet
from app.utils.helpers.task_helpers import save_task, get_tasks_dict_grouped_by
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.utils.helpers.payment_helpers import is_paid, initialize_payment, debit_wallet


class TaskController:
    @staticmethod
    def get_tasks():
        error = False
        
        try:
            tasks = Task.query.filter_by(payment_status='Complete').all()
            all_task_dict = [task.to_dict() for task in tasks]
            msg = 'All Tasks fetched successfully'
            status_code = 200
            extra_data = {
                'Total': len(all_task_dict),
                'all_task': all_task_dict
            }
        except Exception as e:
            error = True
            msg = 'Error getting all tasks'
            status_code = 500
            logging.exception("An exception trying to get all Tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_single_task(task_id):
        error = False
        
        try:
            task = Task.query.get(task_id)
            if task is None:
                return error_response('Task not found', 404)
            
            task_dict = task.to_dict()
            
            msg = 'Task fetched successfully'
            status_code = 200
            extra_data = {
                'task': task_dict
            }
        except Exception as e:
            error = True
            msg = 'Error getting task'
            status_code = 500
            logging.exception("An exception occurred trying to get task:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_advert_tasks():
        error = False
        
        try:
            tasks = AdvertTask.query.filter_by(payment_status='Complete').all()
            all_task_dict = [task.to_dict() for task in tasks]
            msg = 'All Advert Tasks fetched successfully'
            status_code = 200
            extra_data = {
                'Total': len(all_task_dict),
                'all_task': all_task_dict
            }
        except Exception as e:
            error = True
            msg = 'Error getting all tasks'
            status_code = 500
            logging.exception("An exception occurred trying to get all Tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def get_engagement_tasks():
        try:
            tasks = EngagementTask.query.filter_by(payment_status='Complete').all()
            all_task_dict = [task.to_dict() for task in tasks]
            msg = 'All Engagement Tasks fetched successfully'
            status_code = 200
            extra_data = {
                'Total': len(all_task_dict),
                'all_task': all_task_dict
            }
        except Exception as e:
            error = True
            msg = 'Error getting all tasks'
            status_code = 500
            logging.exception("An exception trying to get all Tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_advert_tasks_by(field):
        error = False
        
        try:
            tasks_by_field = get_tasks_dict_grouped_by(field, 'advert')
            
            if len(tasks_by_field) < 1:
                return success_response('There are no advert tasks yet', 200)
            
            msg = f'Advert tasks grouped by {field} fetched successfully.'
            status_code = 200
            extra_data = {
                f'tasks_by_{field}': tasks_by_field,
            }
        except ValueError as e:
            error = True
            msg = f'{e}'
            status_code = 500
            logging.exception(f"An exception occurred getting tasks grouped by {field}:\n", str(e))
        except Exception as e:
            error = True
            msg = f'An error occurred getting tasks grouped by {field}: {e}'
            status_code = 500
            logging.exception(f"An exception occurred getting tasks grouped by {field}:\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_engagement_tasks_by(field):
        error = False
        
        try:
            tasks_by_field = get_tasks_dict_grouped_by(field, 'engagement')
            
            if len(tasks_by_field) < 1:
                return success_response('There are no Engagement tasks yet', 200)
            
            msg = f'Engagement tasks grouped by {field} fetched successfully.'
            status_code = 200
            extra_data = {
                f'tasks_by_{field}': tasks_by_field,
            }
        except ValueError as e:
            error = True
            msg = f'{e}'
            status_code = 500
            logging.exception(f"An exception occurred getting tasks grouped by {field}:\n", str(e))
        except Exception as e:
            error = True
            msg = f'An error occurred getting tasks grouped by goal: {e}'
            status_code = 500
            logging.exception(f"An exception occurred getting tasks grouped by {field}:\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def create_task():
        error = False
    
        try:
            data = request.form.to_dict()
            amount = int(data.get('amount'))
            task_ref = f"task-{generate_random_string(8)}"
            payment_method = request.args.get('payment_method', 'trendit_wallet')
            current_user_id = get_jwt_identity()
            
            
            if payment_method == 'payment_gateway':
                new_task = save_task(data, task_ref)
                if new_task is None:
                    return error_response('Error creating new task', 500)
                
                return initialize_payment(current_user_id, data, payment_type='task_creation', meta_data={'task_ref': task_ref})
            
            if payment_method == 'trendit_wallet':
                # Debit the user's wallet
                try:
                    debit_wallet(current_user_id, amount)
                except ValueError as e:
                    msg = f'Error creating new Task: {e}'
                    return error_response(msg, 400)
                
                new_task = save_task(data, task_ref, payment_status='Complete')
                if new_task is None:
                    return error_response('Error creating new task', 500)
                
                status_code = 201
                msg = 'Task paid for and created successfully'
                extra_data = {'task': new_task.to_dict()}
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error creating new task"
            logging.exception("An exception occurred during creation of Task.\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)

