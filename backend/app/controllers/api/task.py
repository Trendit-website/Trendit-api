import logging
from flask import request
from flask_jwt_extended import get_jwt_identity

from config import Config
from ...models import Task, AdvertTask, EngagementTask, TaskPaymentStatus, TaskStatus, Trendit3User
from ...utils.helpers.task_helpers import save_task, get_tasks_dict_grouped_by_field, fetch_task, get_aggregated_task_counts_by_field
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.payment_helpers import initialize_payment, debit_wallet



class TaskController:
    # ALL TASKS
    @staticmethod
    def get_all_aggregated_task_counts(field):
        
        error = False
        try:
            aggregated_task_counts = get_aggregated_task_counts_by_field(field)
            
            if len(aggregated_task_counts) < 1:
                return success_response('There are no advert tasks yet', 200)
            
            msg = f'All task counts grouped by {field} retrieved successfully.'
            status_code = 200
            extra_data = {
                f'{field}s': aggregated_task_counts,
            }
        except ValueError as e:
            error = True
            msg = f'{e}'
            status_code = 500
            logging.exception(f"An exception occurred getting aggregated task counts grouped by {field}:\n", str(e))
        except Exception as e:
            error = True
            msg = f'An error occurred getting aggregated task counts grouped by {field}: {e}'
            status_code = 500
            logging.exception(f"An exception occurred getting aggregated task counts grouped by {field}:\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_current_user_tasks():
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = Task.query.filter_by(trendit3_user_id=current_user_id) \
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
                return success_response(f'No task has been created yet', 200, extra_data)
            
            api_response = success_response('All Tasks fetched successfully', 200, extra_data)
        except Exception as e:
            log_exception("An exception trying to get all Tasks by current user", e)
            api_response = error_response('Error getting all tasks', 500)
        
        return api_response
    
    
    @staticmethod
    def get_current_user_tasks_by_status(status):
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(5)
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            if not status:
                return error_response('status parameter required', 400)
            
            try:
                # Convert string to enum value (handle potential errors)
                status_enum = TaskStatus(status)
            except ValueError:
                return error_response(f'Invalid status provided: {status}', 400)
            
            pagination = Task.query.filter_by(trendit3_user_id=current_user_id, status=status_enum) \
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
                return success_response(f'There are no {status} task.', 200, extra_data)
            
            msg = f"All {status} Tasks fetched successfully"
            api_response = success_response(msg, 200, extra_data)
        except Exception as e:
            log_exception(f"An exception occurred trying to get all {status} tasks", e)
            api_response = error_response(f"Error getting all {status} tasks", 500)
        
        return api_response
    
    
    @staticmethod
    def get_tasks():
        error = False
        
        try:
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = Task.query.filter_by(payment_status=TaskPaymentStatus.COMPLETE) \
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
    
    
    
    # ADVERT TASKS
    @staticmethod
    def get_current_user_advert_tasks():
        error = False
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = AdvertTask.query.filter_by(trendit3_user_id=current_user_id) \
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
                return success_response(f'No advert tasks have been created', 200, extra_data)
            
            msg = 'All Advert Tasks fetched successfully'
            status_code = 200
            
        except Exception as e:
            error = True
            msg = 'Error getting all advert tasks'
            status_code = 500
            log_exception("An exception occurred trying to get all Advert Tasks", e)
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
            pagination = AdvertTask.query.filter_by(payment_status=TaskPaymentStatus.COMPLETE) \
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
    def get_advert_tasks_by_platform(platform):
        error = False
        
        try:
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = AdvertTask.query.filter_by(payment_status=TaskPaymentStatus.COMPLETE, platform=platform) \
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
    def get_advert_aggregated_task_counts(field):
        """Retrieves aggregated task counts for advert tasks, grouped by the specified field.

        Args:
            field (str): The field to group tasks by. Must be a valid attribute of the AdvertTask model.

        Returns:
            JSON: A JSON object containing the following fields:
                -- message (str): A success message indicating successful retrieval.
                -- status (str): "success"
                -- status_code (int): 200
                -- task_<field>s (list): A list of dictionaries, each containing:
                    -- name (str): The value of the grouped field.
                    -- task_count (int): The number of tasks associated with that field value.

        Raises:
            ValueError: If an invalid field is provided.
            Exception: If an unexpected error occurs during retrieval.
        """
        
        error = False
        try:
            aggregated_task_counts = get_aggregated_task_counts_by_field(field, 'advert')
            
            if len(aggregated_task_counts) < 1:
                return success_response('There are no advert tasks yet', 200)
            
            msg = f'Advert task counts grouped by {field} retrieved successfully.'
            status_code = 200
            extra_data = {
                f'{field}s': aggregated_task_counts,
            }
        except ValueError as e:
            error = True
            msg = f'{e}'
            status_code = 500
            logging.exception(f"An exception occurred getting aggregated task counts grouped by {field}:\n", str(e))
        except Exception as e:
            error = True
            msg = f'An error occurred getting aggregated task counts grouped by {field}: {e}'
            status_code = 500
            logging.exception(f"An exception occurred getting aggregated task counts grouped by {field}:\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    
    # ENGAGEMENT TASKS
    @staticmethod
    def get_engagement_tasks():
        error = False
        try:
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(Config.TASKS_PER_PAGE)
            pagination = EngagementTask.query.filter_by(payment_status=TaskPaymentStatus.COMPLETE) \
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
    def get_engagement_aggregated_task_counts(field):
        
        error = False
        try:
            aggregated_task_counts = get_aggregated_task_counts_by_field(field, 'engagement')
            
            if len(aggregated_task_counts) < 1:
                return success_response('There are no engagement tasks yet', 200)
            
            msg = f'Engagement task counts grouped by {field} retrieved successfully.'
            status_code = 200
            extra_data = {
                f'{field}s': aggregated_task_counts,
            }
        except ValueError as e:
            error = True
            msg = f'{e}'
            status_code = 500
            logging.exception(f"An exception occurred getting aggregated task counts grouped by {field}:\n", str(e))
        except Exception as e:
            error = True
            msg = f'An error occurred getting aggregated task counts grouped by {field}: {e}'
            status_code = 500
            logging.exception(f"An exception occurred getting aggregated task counts grouped by {field}:\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    
    # CREATE NEW TASK
    @staticmethod
    def create_task():
        try:
            data = request.form.to_dict()
            amount = int(data.get('amount'))
            payment_method = request.args.get('payment_method', 'trendit_wallet')
            current_user_id = get_jwt_identity()
            
            
            if payment_method == 'payment_gateway':
                callback_url = request.headers.get('CALLBACK-URL')
                if not callback_url:
                    return error_response('callback URL not provided in the request headers', 400)
                data['callback_url'] = callback_url # add callback url to data
                
                new_task = save_task(data)
                if new_task is None:
                    return error_response('Error creating new task', 500)
                
                return initialize_payment(current_user_id, data, payment_type='task-creation', meta_data={'task_key': new_task.task_key})
            
            if payment_method == 'trendit_wallet':
                # Debit the user's wallet
                try:
                    debit_wallet(current_user_id, amount, 'task-creation')
                except ValueError as e:
                    msg = f'Error creating new Task: {e}'
                    return error_response(msg, 400)
                
                new_task = save_task(data, payment_status=TaskPaymentStatus.COMPLETE)
                if new_task is None:
                    return error_response('Error creating new task', 500)
                
                msg = 'Task created successfully. Payment made using Trendit³ Wallet.'
                extra_data = {'task': new_task.to_dict()}
                
                api_response = success_response(msg, 201, extra_data)
        except TypeError as e:
            log_exception(f"A TypeError occurred during creation of Task", e)
            api_response = error_response(f"TypeError occurred: {str(e)}", 400)
        except Exception as e:
            logging.exception(f"An exception occurred during creation of Task ==> {str(e)}")
            api_response = error_response("Error creating new task", 500)
        
        return api_response


    @staticmethod
    def get_task_metrics():
        try:
            current_user_id = int(get_jwt_identity())
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            all_time_total_tasks = user.total_tasks
            month_start_total_tasks = user.total_tasks
            
        except Exception as e:
            log_exception("An exception occurred getting task metrics", e)
            api_response = error_response("Error getting task metrics", 500)
        
        return api_response