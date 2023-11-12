import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.models.task import Task, AdvertTask, EngagementTask, TaskPerformance
from app.models.payment import Wallet
from app.utils.helpers.task_helpers import save_task
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
            logging.exception("An exception trying to get all Tasks:\n", str(e))
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
    def create_task():
        error = False
    
        try:
            data = request.form.to_dict()
            amount = data.get('amount')
            task_ref = f"task-{generate_random_string(8)}"
            payment_method = request.args.get('payment_method', 'trendit_wallet')
            current_user_id = get_jwt_identity()
            
            new_task = save_task(data, task_ref)
            
            if payment_method == 'payment_gateway':
                return initialize_payment(current_user_id, data, payment_type='task_creation', meta_data={'task_ref': task_ref})
            
            if payment_method == 'trendit_wallet':
                # Debit the user's wallet
                try:
                    debit_wallet(current_user_id, amount)
                except ValueError as e:
                    msg = f'Error creating new Task: {e}'
                    return error_response(msg, 400)
                
                new_task.update(payment_status='Complete')
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

