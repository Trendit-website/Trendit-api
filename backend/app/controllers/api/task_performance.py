import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import Trendit3User
from app.models.task import TaskPerformance, Task
from app.utils.helpers.task_helpers import save_performed_task, fetch_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log


class TaskPerformanceController:
    @staticmethod
    def perform_task():
        error = False
        
        try:
            user_id = int(get_jwt_identity())
            data = request.form.to_dict()
            
            task_id_key = data.get('task_id_key', '')
            task = fetch_task(task_id_key)
            if task is None:
                return error_response('Task not found', 404)
            
            task_id = task.id
            
            performedTask = TaskPerformance.query.filter_by(user_id=user_id, task_id=task_id).first()
            if performedTask:
                return error_response(f"Task already performed and cannot be repeated", 409)
            
            new_performed_task = save_performed_task(data)
            
            if new_performed_task is None:
                return error_response('Error performing task', 500)
            
            status_code = 201
            msg = 'Task Performed successfully'
            extra_data = {'performed_task': new_performed_task.to_dict()}
        except ValueError as e:
            error =  True
            msg = str(e)
            status_code = 404
            logging.exception("An exception occurred trying to create performed tasks:\n", str(e))
        except Exception as e:
            error = True
            msg = f'Error performing task: {e}'
            status_code = 500
            logging.exception("An exception occurred trying to create performed tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_current_user_performed_tasks():
        error = False
        
        try:
            current_user_id = int(get_jwt_identity())
            performed_tasks = TaskPerformance.query.filter(TaskPerformance.user_id == current_user_id).all()
            pt_dict = [pt.to_dict() for pt in performed_tasks]
            msg = 'All Tasks Performed by current user fetched successfully'
            status_code = 200
            extra_data = {
                'total': len(pt_dict),
                'all_performed_tasks': pt_dict
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
            current_user_id = int(get_jwt_identity())
            performed_task = TaskPerformance.query.filter(TaskPerformance.id == pt_id, TaskPerformance.user_id == current_user_id).first()
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            pt_dict = performed_task.to_dict()
            
            msg = 'Task Performed by current user fetched successfully'
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
            
            current_user_id = int(get_jwt_identity())
            performed_task = TaskPerformance.query.filter(TaskPerformance.id == pt_id, TaskPerformance.user_id == current_user_id).first()
            
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            updated_performed_task = save_performed_task(data, pt_id, 'pending')
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
            current_user_id = int(get_jwt_identity())
            performed_task = TaskPerformance.query.filter(TaskPerformance.id == pt_id, TaskPerformance.user_id == current_user_id).first()
            
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

