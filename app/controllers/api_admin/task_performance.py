import logging
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError )

from ...extensions import db
from ...models import TaskPerformance, Task
from ...utils.helpers.mail_helpers import send_task_performance_email
from ...utils.helpers.basic_helpers import log_exception, console_log
from ...utils.helpers.task_helpers import update_performed_task, fetch_performed_task
from ...utils.payments.wallet import credit_wallet
from ...utils.helpers.response_helpers import error_response, success_response


class AdminTaskPerformanceController:
    @staticmethod
    def get_all_performed_tasks():
        error = False
        
        try:
            performed_tasks = TaskPerformance.query.all()
            pt_dict = [pt.to_dict() for pt in performed_tasks]
            msg = 'All Performed Tasks fetched successfully'
            status_code = 200
            extra_data = {
                'total': len(pt_dict),
                'all_performed_task': pt_dict
            }
        except Exception as e:
            error = True
            msg = 'Error getting all performed tasks'
            status_code = 500
            logging.exception("An exception occurred trying to get all performed tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_performed_task(pt_id):
        error = False
        
        try:
            performed_task = TaskPerformance.query.get(pt_id)
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            pt_dict = performed_task.to_dict()
            
            msg = 'Performed Task fetched successfully'
            status_code = 200
            extra_data = {
                'performed_task': pt_dict
            }
        except Exception as e:
            error = True
            msg = 'Error getting performed tasks'
            status_code = 500
            logging.exception("An exception occurred trying to get performed tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def update_performed_task(pt_id):
        error = False
        
        try:
            data = request.form.to_dict()
            performed_task = TaskPerformance.query.get(pt_id)
            
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            updated_performed_task = update_performed_task(data, pt_id, 'pending')
            if updated_performed_task is None:
                return error_response('Error updating performed task', 500)
            
            status_code = 200
            msg = 'Performed Task updated successfully'
            extra_data = {'performed_task': updated_performed_task.to_dict()}
        except ValueError as e:
            error =  True
            msg = f'error occurred updating performed task: {str(e)}'
            status_code = 500
            logging.exception("An exception occurred trying to create performed tasks:", str(e))
        except Exception as e:
            error = True
            msg = f'Error updating performed task: {e}'
            status_code = 500
            logging.exception("An exception occurred trying to update performed tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def delete_performed_task(pt_id):
        error = False
        
        try:
            performed_task = TaskPerformance.query.get(pt_id)
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            performed_task.delete()
            msg = 'Performed task deleted successfully'
            status_code = 200
        except Exception as e:
            error = True
            msg = 'Error deleting performed tasks'
            status_code = 500
            db.session.rollback()
            logging.exception("An exception occurred trying to delete performed tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code)


    @staticmethod
    def verify_performed_task():
        try:
            data = request.get_json()
            status = data.get("status", "")
            pt_id_key = data.get("performed_task_id_key")
            
            if not status or not pt_id_key:
                return error_response("The field 'status' or 'performed_task_id_key' must be provided", 400)
            
            performed_task = fetch_performed_task(pt_id_key)
            if not performed_task:
                return error_response("Performed Task not found", 404)
            
            
            if status not in ["accept", "reject"]:
                return error_response("status not allowed", 400)
            
            status_val = "completed" if status == "accept" else "rejected"
            
            performed_task.update(status=status_val)
            
            if status_val == "completed":
                user_id = performed_task.user_id
                credit_wallet(user_id, performed_task.reward_money)
            
            extra_data = {"performed_task": performed_task.to_dict()}
            
            api_response = success_response(f"Performed Task {status}ed", 200, extra_data)
            
            send_task_performance_email(pt_id=performed_task.id)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during registration', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            api_response = error_response("An unexpected error occurred. Our developers are looking into this.", 500)
            log_exception("An exception occurred trying to get task:", e)
        
        return api_response
