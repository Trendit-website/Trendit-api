import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import TaskPerformance, Task
from app.utils.helpers.task_helpers import update_performed_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.models.task import TaskStatus, TaskPaymentStatus
from app.models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails


class AdminTaskController:
    @staticmethod
    def get_all_tasks():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 15, type=int)
            
            tasks = Task.query.paginate(page=page, per_page=per_page, error_out=False)
            
            if page > tasks.pages:
                return success_response('No content', 204, {'tasks': []})
            
            task_list = [task.to_dict() for task in tasks.items]
            
            extra_data = {
                'total': tasks.total,
                'pages': tasks.pages,
                'tasks': task_list
            }

            return success_response('All tasks fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception("An exception occurred trying to get all tasks:\n", str(e))
            return error_response('Error getting all tasks', 500)
        
    @staticmethod
    def get_all_failed_tasks():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 15, type=int)
            
            tasks = Task.query.filter_by(status=TaskStatus.DECLINED).paginate(page=page, per_page=per_page, error_out=False)
            
            if page > tasks.pages:
                return success_response('No content', 204, {'tasks': []})
            
            task_list = [task.to_dict() for task in tasks.items]
            
            extra_data = {
                'total': tasks.total,
                'pages': tasks.pages,
                'tasks': task_list
            }

            return success_response('All failed tasks fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception("An exception occurred trying to get all failed tasks:\n", str(e))
            return error_response('Error getting all failed tasks', 500)


    @staticmethod
    def get_all_approved_tasks():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 15, type=int)
            
            tasks = Task.query.filter_by(status=TaskStatus.APPROVED).paginate(page=page, per_page=per_page, error_out=False)
            
            if page > tasks.pages:
                return success_response('No content', 204, {'tasks': []})
            
            task_list = [task.to_dict() for task in tasks.items]
            
            extra_data = {
                'total': tasks.total,
                'pages': tasks.pages,
                'tasks': task_list
            }

            return success_response('All approved tasks fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception("An exception occurred trying to get all approved tasks:\n", str(e))
            return error_response('Error getting all approved tasks', 500)
        

    @staticmethod
    def get_all_pending_tasks():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 15, type=int)
            
            tasks = Task.query.filter_by(status=TaskStatus.PENDING).paginate(page=page, per_page=per_page, error_out=False)
            
            if page > tasks.pages:
                return success_response('No content', 204, {'tasks': []})
            
            task_list = [task.to_dict() for task in tasks.items]
            
            extra_data = {
                'total': tasks.total,
                'pages': tasks.pages,
                'tasks': task_list
            }

            return success_response('All pending tasks fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception("An exception occurred trying to get all pending tasks:\n", str(e))
            return error_response('Error getting all pending tasks', 500)


    @staticmethod
    def approve_task(task_id: int):
        try:
            task = Task.query.get(task_id).to_dict()
            if task is None:
                return error_response('Task not found', 404)
                        
            task_description = task.get('caption', '')
            task_time = task.get('date_created')
            task_type = task.get('task_type')
            task.status = TaskStatus.APPROVED
            db.session.commit()
            
            email = Trendit3User.query.get(task.trendit3_user_id).email

            try:
                send_other_emails(
                    email, 
                    email_type='task_approved',
                    task_description=task_description,
                    task_time=task_time,
                    task_type=task_type
                ) # send email
            except Exception as e:
                return error_response('Error occurred sending Email', 500)
            
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
            task.status = TaskStatus.DECLINED
            db.session.commit()
            
            email = Trendit3User.query.get(task.trendit3_user_id).email

            try:
                send_other_emails(email, email_type='task_rejected') # send email
            except Exception as e:
                return error_response('Error occurred sending Email', 500)
            
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