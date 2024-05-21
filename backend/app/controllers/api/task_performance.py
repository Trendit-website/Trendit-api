import logging
from flask import request
from sqlalchemy import not_
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...models import Trendit3User
from ...models.task import TaskPerformance
from ...utils.helpers.task_helpers import save_performed_task, fetch_task, generate_random_task, initiate_task, fetch_performed_task
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...exceptions import PendingTaskError, NoUnassignedTaskError


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
        try:
            data = request.get_json()
            task_type = data.get('task_type')
            filter_value = data.get('platform') or data.get('goal', '')
            
            random_task = generate_random_task(task_type, filter_value)
            
            # Initiate task performance
            Initiated_task = initiate_task(random_task)
            
            msg = f'An {task_type.capitalize()} task for {filter_value} generated successfully.'
            extra_data = {'generated_task': Initiated_task}
            
            api_response = success_response(msg, 200, extra_data)
        except PendingTaskError as e:
            api_response = error_response(f'{e}', 409)
        except NoUnassignedTaskError as e:
            api_response = error_response(f'{e}', 206)
        except ValueError as e:
            api_response = error_response(f'{e}', 400)
        except AttributeError as e:
            log_exception("An exception occurred generating random task", e)
            api_response = error_response(f'{e}', 500)
        except Exception as e:
            log_exception("An exception occurred generating random task for the user", e)
            api_response = error_response(f'An error occurred generating random task: {e}', 500)
        
        return api_response
    
    
    @staticmethod
    def perform_task():
        try:
            current_user_id = int(get_jwt_identity())
            data = request.form.to_dict()
            
            task_id_key = data.get('task_id_key', '')
            
            if not task_id_key:
                return error_response("task key or id must be provided", 400)
            
            task = fetch_task(task_id_key)
            if task is None:
                return error_response('Task not found', 404)
            
            task_id = task.id
            
            console_log('current_user_id', current_user_id)
            
            # check if user has a performed task already done
            performedTask = TaskPerformance.query.filter_by(user_id=current_user_id, task_id=task_id).filter(not_(TaskPerformance.status == 'pending')).first()
            
            console_log('performedTask', performedTask)
            
            if performedTask:
                console_log('performedTask status', performedTask.status)
                return error_response(f"Task already performed and cannot be repeated", 409)
            
            new_performed_task = save_performed_task(data, status='in_review')
            
            if new_performed_task is None:
                return error_response('Error performing task', 500)
            
            msg = 'Task Performed successfully'
            extra_data = {'performed_task': new_performed_task.to_dict()}
            
            api_response = success_response(msg, 201, extra_data)
        except ValueError as e:
            log_exception("An exception occurred trying to create performed tasks", e)
            return success_response(str(e), 404)
        except Exception as e:
            log_exception("An exception occurred trying to create performed tasks", e)
            return success_response(f'Error performing task: {e}', 500)
        finally:
            db.session.close()
        
        return api_response
    
    
    @staticmethod
    def get_current_user_performed_tasks():
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            per_page = 10
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            # Fetch all performed tasks for current user
            pagination = TaskPerformance.query.filter_by(user_id=current_user_id) \
                .order_by(TaskPerformance.started_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            performed_tasks = pagination.items
            current_performed_tasks = [performed_task.to_dict() for performed_task in performed_tasks]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "performed_tasks": current_performed_tasks,
            }
            
            if not performed_tasks:
                return success_response(f'No task has been performed yet', 200, extra_data)
            
            msg = 'All performed tasks fetched successfully'
            api_response = success_response(msg, 200, extra_data)
        except Exception as e:
            log_exception("An exception occurred trying to get all performed tasks", e)
            return error_response("Error getting all performed tasks", 500)
        
        return api_response
    
    
    @staticmethod
    def get_user_performed_tasks_by_status(status):
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(6)
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            pagination = TaskPerformance.query.filter_by(user_id=current_user_id, status=status) \
                .order_by(TaskPerformance.started_at.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            console_log("pagination", pagination)
            
            performed_tasks = pagination.items
            console_log(f"{status} Task", performed_tasks)
            
            current_performed_tasks = [performed_task.to_dict() for performed_task in performed_tasks]
            console_log("current_performed_tasks", current_performed_tasks)
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "performed_tasks": current_performed_tasks,
            }
            
            if not performed_tasks:
                return success_response(f'There are no {status} performed tasks.', 200, extra_data)
            
            msg = f"All {status} Performed Tasks fetched successfully"
            api_response = success_response(msg, 200, extra_data)
        except Exception as e:
            msg = f"Error getting all {status} performed tasks"
            log_exception(f"An exception occurred trying to get all {status} performed tasks", e)
            return error_response(msg, 500)
        
        return api_response
    
    
    
    @staticmethod
    def get_performed_task(pt_id_key):
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            performed_task = fetch_performed_task(pt_id_key)
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            if performed_task.user_id != current_user_id:
                return error_response('You are not authorized to fetch this performed task', 401)
            
            pt_dict = performed_task.to_dict()
            
            msg = 'Task Performed by current user fetched successfully'
            extra_data = {'performed_task': pt_dict}
            api_response = success_response(msg, 200, extra_data)
        except Exception as e:
            msg = 'Error getting performed tasks'
            log_exception("An exception occurred trying to get performed tasks", e)
            return error_response(msg, 500)
        
        return api_response
    
    
    @staticmethod
    def update_performed_task(pt_id_key):
        try:
            data = request.form.to_dict()
            current_user_id = int(get_jwt_identity())
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            performed_task = fetch_performed_task(pt_id_key)
            
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            if performed_task.user_id != current_user_id:
                return error_response('You are not authorized to update this performed task', 401)
            
            updated_performed_task = save_performed_task(data, performed_task.id, 'pending')
            if updated_performed_task is None:
                return error_response('Error updating performed task', 500)
            
            msg = 'Performed Task updated successfully'
            extra_data = {'performed_task': updated_performed_task.to_dict()}
            api_response = success_response(msg, 200, extra_data)
        except ValueError as e:
            msg = f'error occurred updating performed task: {str(e)}'
            log_exception("An exception occurred trying to create performed tasks", e)
            return error_response(msg, 500)
        except Exception as e:
            msg = f'Error updating performed task: {e}'
            log_exception("An exception occurred trying to update performed tasks", str(e))
            return error_response(msg, 500)
        
        return api_response


    @staticmethod
    def delete_performed_task(pt_id_key):
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            performed_task = fetch_performed_task(pt_id_key)
            
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            if performed_task.user_id != current_user_id:
                return error_response('You are not authorized to update this performed task', 401)
            
            performed_task.delete()
            msg = 'Performed task deleted successfully'
            api_response = success_response(msg, 200)
        except Exception as e:
            db.session.rollback()
            msg = "Error deleting performed tasks"
            log_exception("An exception occurred trying to delete performed tasks", e)
            return error_response(msg, 500)
        
        return api_response


    @staticmethod
    def cancel_performed_task(pt_id_key):
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            performed_task = fetch_performed_task(pt_id_key)
            
            if performed_task is None:
                return error_response('Performed task not found', 404)
            
            if performed_task.user_id != current_user_id:
                return error_response('You are not authorized to cancel this performed task', 401)
            
            performed_task.update(status='cancelled')
            msg = 'Performed task canceled successfully'
            api_response = success_response(msg, 200)
        except Exception as e:
            db.session.rollback()
            msg = "Error deleting performed tasks"
            log_exception("An exception occurred trying to delete performed tasks", e)
            return error_response(msg, 500)
        
        return api_response

