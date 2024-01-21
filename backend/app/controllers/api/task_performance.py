import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import TaskPerformance
from app.utils.helpers.task_helpers import save_performed_task, fetch_task, generate_random_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import console_log
from app.exceptions import PendingTaskError, NoUnassignedTaskError


class TaskPerformanceController:
    @staticmethod
    def generate_task():
        """Retrieves a random task of the specified type and platform, ensuring it's not assigned to another user.

        requests json data:
            task_type (str): The type of task to retrieve ('advert' or 'engagement').
            platform (str): The platform to filter tasks by.

        Returns:
            JSON: A JSON object containing the randomly selected task and success message.

        Raises:
            ValueError: If an invalid task type or platform is provided.
            Exception: If an unexpected error occurs during retrieval.
        """
        error = False
        try:
            data = request.get_json()
            task_type = data.get('task_type')
            filter_value = data.get('platform') or data.get('goal', '')
            
            random_task = generate_random_task(task_type, filter_value)
            
            msg = f'An unassigned {task_type.capitalize()} task for {filter_value} retrieved successfully.'
            status_code = 200
            extra_data = {
                'generated_task': random_task,
            }
        except PendingTaskError as e:
            error = True
            msg = f'{e}'
            status_code = 409
            logging.exception(f"An exception occurred generating random task:", str(e))
        except NoUnassignedTaskError as e:
            error = True
            msg = f'{e}'
            status_code = 200
            logging.exception(f"An exception occurred generating random task:", str(e))
        except AttributeError as e:
            error = True
            msg = f'{e}'
            status_code = 500
            logging.exception(f"An exception occurred generating random task:", str(e))
        except Exception as e:
            error = True
            msg = f'An error occurred generating random task: {e}'
            status_code = 500
            logging.exception(f"An exception occurred generating random task for the user:", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def initiate_task(task_id_key):
        error = False
        
        try:
            current_user_id = int(get_jwt_identity())
            
            # Retrieve the specified task.
            task = fetch_task(task_id_key)
            if task is None:
                return error_response('Task not found', 404)
            
            # Validate task readiness (adjust criteria as needed)
            if task.assigned_user_id or task.payment_status != 'Complete':
                raise ValueError("This task is not available for performance")
            
            # Create a new TaskPerformance instance
            task_performance = TaskPerformance(
                task_id=task.id,
                task_type=task.type,
                user_id=current_user_id,
                status='pending'
            )
            db.session.add(task_performance)
            db.session.commit()
            
            # Mark the original task as assigned
            task.assigned_user_id = current_user_id
            db.session.add(task)
            db.session.commit()

            return success_response(
                f"Task initiation successful. Task performance ID: {task_performance.key}",
                200,
                extra_data={'task_performance': task_performance.to_dict()}
            )
        except Exception as e:
            error = True
            msg = f'task could not be initiated: {e}'
            status_code = 500
            db.session.rollback()
            logging.exception(f"An exception occurred initiating task:", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('Task initiated successfully', 200)
    
    
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
            
            new_performed_task = save_performed_task(data, status='in_review')
            
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
    def get_user_performed_tasks_by_status(status):
        error = False
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(6)
            pagination = TaskPerformance.query.filter_by(user_id=current_user_id, status=status) \
                .order_by(TaskPerformance.started_at.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            
            performed_tasks = pagination.items
            current_tasks = [performed_task.to_dict() for performed_task in performed_tasks]
            extra_data = {
                'total': pagination.total,
                "performed_tasks": current_tasks,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not performed_tasks:
                return success_response(f'There are no {status} performed tasks.', 200, extra_data)
            
            msg = f'All {status} Performed Tasks fetched successfully'
            status_code = 200
        except Exception as e:
            error = True
            msg = f'Error getting all {status} performed tasks'
            status_code = 500
            logging.exception(f"An exception occurred trying to get all {status} performed tasks: ==>", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    
    @staticmethod
    def get_performed_task(pt_id):
        error = False
        
        try:
            current_user_id = int(get_jwt_identity())
            performed_task = TaskPerformance.query.filter(TaskPerformance.id == pt_id).first()
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

