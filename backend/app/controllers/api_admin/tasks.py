import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import TaskPerformance, Task
from app.utils.helpers.task_helpers import save_performed_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log


class AdminTaskController:
    @staticmethod
    def get_all_tasks():
        try:
            tasks = Task.query.all()
            task_list = []
            for task in tasks:
                task_list.append(task.to_dict())
            extra_data = {
                'total': len(task_list),
                'tasks': task_list
            }

            return success_response('All tasks fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception("An exception occurred trying to get all tasks:\n", str(e))
            return error_response('Error getting all tasks', 500)
        

    @staticmethod
    def approve_task(task_id: int):
        try:
            task = Task.query.get(task_id)
            if task is None:
                return error_response('Task not found', 404)
            task.approved = True
            db.session.commit()
            return success_response('Task approved successfully', 200)
        except Exception as e:
            logging.exception("An exception occurred trying to approve task:\n", str(e))
            return error_response('Error approving task', 500)
        
    
    @staticmethod
    def reject_task(task_id: int):
        try:
            task = Task.query.get(task_id)
            if task is None:
                return error_response('Task not found', 404)
            task.approved = False
            db.session.commit()
            return success_response('Task rejected successfully', 200)
        except Exception as e:
            logging.exception("An exception occurred trying to reject task:\n", str(e))
            return error_response('Error rejecting task', 500)
        

    @staticmethod
    def get_task(task_id: int):
        try:
            task = Task.query.get(task_id)
            if task is None:
                return error_response('Task not found', 404)
            extra_data = {
                'task': task.to_dict()
            }
            return success_response('Task fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception("An exception occurred trying to get task:\n", str(e))
            return error_response('Error getting task', 500)