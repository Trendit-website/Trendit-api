import logging
from flask import request
from flask_jwt_extended import get_jwt_identity

from config import Config
from app.models.task import Task, AdvertTask, EngagementTask
from app.utils.helpers.task_helpers import save_task, get_tasks_dict_grouped_by_field, fetch_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.utils.helpers.payment_helpers import initialize_payment, debit_wallet


class TaskController:
    @staticmethod
    def get_current_user_tasks():
        error = False
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = Task.query.filter_by(trendit3_user_id=current_user_id, payment_status='Complete') \
                .order_by(Task.date_created.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            tasks = pagination.items
            current_tasks = [task.to_dict() for task in tasks]
            extra_data = {
                'total': pagination.total,
                "all_tasks": current_tasks,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not tasks:
                return success_response(f'User hasn\'t created any task yet', 200, extra_data)
            
            msg = 'All Tasks created by current user fetched successfully'
            status_code = 200
            
        except Exception as e:
            error = True
            msg = 'Error getting all tasks created by current user'
            status_code = 500
            logging.exception("An exception trying to get all Tasks by current user:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_tasks():
        error = False
        
        try:
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = Task.query.filter_by(payment_status='Complete') \
                .order_by(Task.date_created.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            
            tasks = pagination.items
            current_tasks = [task.to_dict() for task in tasks]
            extra_data = {
                'total': pagination.total,
                "all_tasks": current_tasks,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not tasks:
                return success_response(f'There are no tasks yet', 200, extra_data)
            
            msg = 'All Tasks fetched successfully'
            status_code = 200
            
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
    def get_single_task(task_id_key):
        error = False
        
        try:
            task = fetch_task(task_id_key)
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
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = AdvertTask.query.filter_by(payment_status='Complete') \
                .order_by(AdvertTask.date_created.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            tasks = pagination.items
            current_tasks = [task.to_dict() for task in tasks]
            extra_data = {
                'total': pagination.total,
                "advert_tasks": current_tasks,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not tasks:
                return success_response(f'There are no advert tasks yet', 200, extra_data)
            
            msg = 'All Advert Tasks fetched successfully'
            status_code = 200
            
        except Exception as e:
            error = True
            msg = 'Error getting all advert tasks'
            status_code = 500
            logging.exception("An exception occurred trying to get all Advert Tasks:\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def get_engagement_tasks():
        error = False
        try:
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = EngagementTask.query.filter_by(payment_status='Complete') \
                .order_by(EngagementTask.date_created.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            tasks = pagination.items
            current_tasks = [task.to_dict() for task in tasks]
            extra_data = {
                'total': pagination.total,
                "engagement_tasks": current_tasks,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not tasks:
                return success_response(f'There are no engagement tasks yet', 200, extra_data)
            
            msg = 'All Engagement Tasks fetched successfully'
            status_code = 200
            
        except Exception as e:
            error = True
            msg = 'Error getting all engagement tasks'
            status_code = 500
            logging.exception("An exception trying to get all Engagement Tasks:", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_advert_tasks_grouped_by_field(field):
        error = False
        
        try:
            tasks_by_field = get_tasks_dict_grouped_by_field(field, 'advert')
            
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
    def get_advert_tasks_by_platform(platform):
        error = False
        
        try:
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = AdvertTask.query.filter_by(payment_status='Complete', platform=platform) \
                .order_by(AdvertTask.date_created.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            tasks = pagination.items
            current_tasks = [task.to_dict() for task in tasks]
            extra_data = {
                'total': pagination.total,
                "advert_tasks": current_tasks,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not tasks:
                return success_response(f'There are no advert task for {platform} yet', 200, extra_data)
            
            msg = f'All Advert Tasks for {platform} fetched successfully'
            status_code = 200
            
        except Exception as e:
            error = True
            status_code = 500
            msg = f"Error fetching Advert Tasks for {platform} from the database"
            logging.exception(f"An exception occurred during fetching Advert Tasks for {platform}", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_engagement_tasks_grouped_by_field(field):
        error = False
        
        try:
            tasks_by_field = get_tasks_dict_grouped_by_field(field, 'engagement')
            
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
            payment_method = request.args.get('payment_method', 'trendit_wallet')
            current_user_id = get_jwt_identity()
            
            
            if payment_method == 'payment_gateway':
                new_task = save_task(data)
                if new_task is None:
                    return error_response('Error creating new task', 500)
                
                return initialize_payment(current_user_id, data, payment_type='task_creation', meta_data={'task_key': new_task.task_key})
            
            if payment_method == 'trendit_wallet':
                # Debit the user's wallet
                try:
                    debit_wallet(current_user_id, amount)
                except ValueError as e:
                    msg = f'Error creating new Task: {e}'
                    return error_response(msg, 400)
                
                new_task = save_task(data, payment_status='Complete')
                if new_task is None:
                    return error_response('Error creating new task', 500)
                
                status_code = 201
                msg = 'Task created successfully. Payment made using Trendit³ Wallet.'
                extra_data = {'task': new_task.to_dict()}
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error creating new task"
            logging.exception("An exception occurred during creation of Task ==>", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)

