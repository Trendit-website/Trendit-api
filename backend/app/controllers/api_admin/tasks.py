import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import ( DataError, DatabaseError, )

from app.extensions import db
from app.models.task import TaskPerformance, Task, AdvertTask, EngagementTask, TaskPaymentStatus, TaskStatus
from ...utils.helpers.task_helpers import save_task, get_tasks_dict_grouped_by_field, fetch_task, get_aggregated_task_counts_by_field, fetch_performed_task
from app.utils.helpers.task_helpers import update_performed_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log, log_exception
from app.models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails
from ...utils.payments.utils import initialize_payment
from ...utils.payments.wallet import debit_wallet, credit_wallet


class AdminTaskController:
    @staticmethod
    def get_all_tasks():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 15, type=int)
            
            tasks = Task.query.order_by(Task.date_created.desc()).paginate(page=page, per_page=per_page, error_out=False)
            
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
            task = Task.query.get(task_id)
            
            if task is None:
                return error_response('Task not found', 404)
            
            task_dict = task.to_dict()            
            task_description = task_dict.get('caption', '')
            task_time = task_dict.get('date_created')
            task_type = task_dict.get('task_type')
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
    
    @staticmethod
    def get_task_performances(task_id_key):
        try:
            
            task = fetch_task(task_id_key)
            if not task:
                return error_response("Task not found", 404)
            
            
            page = request.args.get("page", 1, type=int)
            per_page = 5
            pagination = TaskPerformance.query.filter_by(task_id=task.id) \
                .order_by(TaskPerformance.started_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            task_performances = pagination.items
            current_task_performances = [task_performance.to_dict() for task_performance in task_performances]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "task_performances": current_task_performances,
            }
            
            if not task_performances:
                return success_response(f'No one has performed this task yet', 200, extra_data)
            
            api_response = success_response("Task performances fetched successfully", 200, extra_data)
        
        except Exception as e:
            api_response = error_response("An unexpected error occurred. Our developers are looking into this.", 500)
            log_exception("An exception occurred trying to get task:", e)
        
        return api_response


    @staticmethod
    def verify_performed_task():
        try:
            current_user_id = int(get_jwt_identity())
            current_user = Trendit3User.query.get(current_user_id)
            
            if not current_user:
                return error_response(f"user not found", 404)
            
            data = request.get_json()
            status = data.get("status", "")
            pt_id_key = data.get("performed_task_id_key")
            
            if not status or not pt_id_key:
                return error_response("The field status or performed_task_id_key must be provided", 400)
            
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
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during registration', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            api_response = error_response("An unexpected error occurred. Our developers are looking into this.", 500)
            log_exception("An exception occurred trying to get task:", e)
        
        return api_response