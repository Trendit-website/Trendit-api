import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import TaskPerformance, Task
from app.utils.helpers.task_helpers import save_performed_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log


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

