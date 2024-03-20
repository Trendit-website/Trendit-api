import sys, logging
from flask import request, jsonify, current_app
from sqlalchemy import func, or_
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import Task, AdvertTask, EngagementTask, TaskPerformance
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.media_helpers import save_media
from app.exceptions import PendingTaskError, NoUnassignedTaskError


def fetch_task(task_id_key):
    """
    Fetches a task from the database based on either its ID or task_key.

    Parameters:
    - task_id_key (int or str): The ID or task_key of the task to fetch. 
        - If an integer, the function fetches the task by ID; 
        - if a string, it fetches the task by task_key.

    Returns:
    - Task or None: The fetched task if found, or None if no task matches the provided ID or task_key.
    """
    try:
        # Check if task_id_key is an integer
        task_id_key = int(task_id_key)
        # Fetch the task by id
        task = Task.query.filter_by(id=task_id_key).first()
    except ValueError:
        # If not an integer, treat it as a string
        task = Task.query.filter_by(task_key=task_id_key).first()

    if task:
        return task
    else:
        return None

def get_tasks_dict_grouped_by_field(field, task_type):
    tasks_dict = {}
    
    try:
        if task_type == 'advert':
            tasks = AdvertTask.query.filter_by(payment_status='complete').all()
        elif task_type == 'engagement':
            tasks = EngagementTask.query.filter_by(payment_status='complete').all()
        else:
            raise ValueError(f"Invalid task_type: {task_type}")

        for task in tasks:
            key = getattr(task, field)
            if key not in tasks_dict:
                tasks_dict[key] = {
                    'total': 0,
                    'tasks': [],
                }
            tasks_dict[key]['total'] += 1
            tasks_dict[key]['tasks'].append(task.to_dict())
    except AttributeError as e:
        raise ValueError(f"Invalid field: {field}")
    except Exception as e:
        raise e

    return tasks_dict


def get_aggregated_task_counts_by_field(field, task_type=None):
    """Retrieves aggregated task counts grouped by the specified field,
    optimized using database-level aggregation, and returns results as a dictionary.

    Args:
        field (str): The field to group tasks by.
        task_type (str): The type of tasks to retrieve ('advert' or 'engagement').

    Returns:
        dict: A dictionary where keys are the field values and values are dictionaries
                containing the field value ('name') and its count ('total').

    Raises:
        ValueError: If an invalid field or task_type is provided.
    """

    try:
        task_model = (AdvertTask if task_type == 'advert' else EngagementTask if task_type == 'engagement' else Task)
        
        results = db.session.query(getattr(task_model, field), func.count(task_model.id).label('task_count')) \
                            .filter_by(payment_status='complete') \
                            .group_by(getattr(task_model, field)) \
                            .all()
        
        return {key: {'name': key, 'total': count} for key, count in results}

    except AttributeError as e:
        raise ValueError(f"Invalid field: {field}")
    except Exception as e:
        raise e


def generate_random_task(task_type, filter_value):
    """Retrieves a random task of the specified type, filtering by platform or goal, ensuring it's not assigned to another user.

        Args:
            task_type (str): The type of task to retrieve ('advert' or 'engagement').
            filter_value (str): The value to filter tasks by (platform for adverts, goal for engagements).

        Returns:
            JSON: A JSON object containing the randomly selected task.

        Raises:
            LookupError: If no unassigned task was found
            ValueError: If an invalid task type or platform is provided.
            Exception: If an unexpected error occurs during retrieval.
    """
    try:
        current_user_id = int(get_jwt_identity())
        performed_task = TaskPerformance.query.filter_by(status='pending', user_id=current_user_id).first()
        
        if performed_task:
            raise PendingTaskError
        
        task_model = (AdvertTask if task_type == 'advert' else EngagementTask if task_type == 'engagement' else None)
        
        # Dynamically filter by platform, goal, posts_count or engagements_count based on task type
        filter_field = 'platform' if task_type == 'advert' else 'goal'
        count_field = 'posts_count' if task_type == 'advert' else 'engagements_count'
        
        # Filter for unassigned tasks
        unassigned_task = task_model.query.filter(
            getattr(task_model, filter_field) == filter_value,
            task_model.payment_status == 'complete',
            getattr(task_model, count_field) > getattr(task_model, 'total_success')
        ).order_by(func.random()).first()
        
        
        if not unassigned_task:
            raise NoUnassignedTaskError(f"There are no unassigned {task_type} tasks for the {filter_field} '{filter_value}'.")
        
        # Initiate task performance
        initiate_task(unassigned_task)
        
        return unassigned_task.to_dict()  # Return the generated task

    except AttributeError as e:
        raise ValueError(f"Invalid Task Type or Filter: {task_type}/{filter_value}")
    except Exception as e:
        raise e


def get_task_by_key(task_key):
    task = EngagementTask.query.filter_by(task_key=task_key).first()

    if task is None:
        task = AdvertTask.query.filter_by(task_key=task_key).first()

    if task is None:
        task = Task.query.filter_by(task_key=task_key).first()
    
    return task


def save_task(data, task_id_key=None, payment_status='Pending'):
    try:
        user_id = int(get_jwt_identity())
        task_type = data.get('task_type', '')
        platform = data.get('platform', '').lower()
        fee = data.get('amount', '')
        
        posts_count_str = data.get('posts_count', '')
        posts_count = int(posts_count_str) if posts_count_str and posts_count_str.isdigit() else 0
        
        target_country = data.get('target_country', '')
        target_state = data.get('target_state', '')
        gender = data.get('gender', '')
        caption = data.get('caption', '')
        hashtags = data.get('hashtags', '')
        media = request.files.get('media', '')
        
        
        goal = data.get('goal','')
        account_link = data.get('account_link', '')
        
        engagements_count_str = data.get('engagements_count', '')
        engagements_count = int(engagements_count_str) if engagements_count_str and engagements_count_str.isdigit() else 0
        
        
        task = None
        if task_id_key:
            task = fetch_task(task_id_key)
        
        if media.filename != '':
            try:
                media_id = save_media(media)
            except Exception as e:
                current_app.logger.error(f"An error occurred while saving media for Task: {str(e)}")
                return None
        elif media.filename == '' and task:
            if task.media_id:
                media_id = task.media_id
            else:
                media_id = None
        else:
            media_id = None
        
        if task_type == 'advert':
            if task:
                task.update(trendit3_user_id=user_id, task_type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, posts_count=posts_count, target_country=target_country, target_state=target_state, gender=gender, caption=caption, hashtags=hashtags)
                
                return task
            else:
                new_task = AdvertTask.create_task(trendit3_user_id=user_id, task_type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, posts_count=posts_count, target_country=target_country, target_state=target_state, gender=gender, caption=caption, hashtags=hashtags)
                
                return new_task
            
        elif task_type == 'engagement':
            if task:
                task.update(trendit3_user_id=user_id, task_type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, goal=goal, account_link=account_link, engagements_count=engagements_count)
                
                return task
            else:
                new_task = EngagementTask.create_task(trendit3_user_id=user_id, task_type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, goal=goal, account_link=account_link, engagements_count=engagements_count)
                
                return new_task
        else:
            return None
    except Exception as e:
        logging.exception(f"An exception occurred trying to save Task {data.get('task_type')}:\n", str(e))
        db.session.rollback()
        console_log('sys excInfo', sys.exc_info())
        return None




def initiate_task(task, status='pending'):
    try:
        current_user_id = int(get_jwt_identity())
        
        if task is None:
            raise NoUnassignedTaskError("Task not found.")
        
        
        # Create a new TaskPerformance instance
        initiated_task = TaskPerformance.create_task_performance(user_id=current_user_id, task_id=task.id, task_type=task.task_type, status=status, reward_money=0.0, proof_screenshot_id=None)
        
        # Mark the task as assigned
        task.total_allocated += 1
        db.session.add(task)
        db.session.commit()
        
        
    except Exception as e:
        db.session.rollback()
        logging.exception("An exception occurred trying to initiate task performance: ==>", str(e))
        raise e


def save_performed_task(data, pt_id=None, status='pending'):
    try:
        user_id = int(get_jwt_identity())
        
        task_id_key = data.get('task_id_key', '')
        task = fetch_task(task_id_key)
        if task is None:
            raise ValueError("Task not found.")
        
        task_id = task.id
        
        reward_money = float(data.get('reward_money'))
        screenshot = request.files['screenshot']
        account_name = data.get('account_name')
        
        
        task_type = task.task_type
        
        performed_task = None
        if pt_id:
            performed_task = TaskPerformance.query.get(pt_id)
            
        if screenshot.filename != '':
            try:
                screenshot_id = save_media(screenshot)
            except Exception as e:
                current_app.logger.error(f"An error occurred while saving Screenshot: {str(e)}")
                raise Exception("Error saving Screenshot.")
        elif screenshot.filename == '' and task:
            if performed_task.proof_screenshot_id:
                screenshot_id = performed_task.proof_screenshot_id
            else:
                raise Exception("No screenshot provided.")
        else:
            raise Exception("No screenshot provided.")
        
        if performed_task:
            performed_task.update(user_id=user_id, task_id=task_id, task_type=task_type, reward_money=reward_money, proof_screenshot_id=screenshot_id, status=status)
            
            return performed_task
        else:
            new_performed_task = TaskPerformance.create_task_performance(user_id=user_id, task_id=task_id, task_type=task_type, reward_money=reward_money, proof_screenshot_id=screenshot_id, account_name=account_name, status=status)
            
            return new_performed_task
    except Exception as e:
        logging.exception("An exception occurred trying to save performed task:\n", str(e))
        db.session.rollback()
        raise e



def fetch_performed_tasks_by_status(status):

    try:
        current_user_id = int(get_jwt_identity())
        page = request.args.get("page", 1, type=int)
        tasks_per_page = int(6)
        pagination = TaskPerformance.query.filter_by(user_id=current_user_id, status=status) \
            .order_by(TaskPerformance.started_at.desc()) \
            .paginate(page=page, per_page=tasks_per_page, error_out=False)
        
        
        performed_tasks = pagination.items
        current_tasks = [performed_task.to_dict() for performed_task in performed_tasks]
        json_data = {
            'total': pagination.total,
            "performed_tasks": current_tasks,
            "current_page": pagination.page,
            "total_pages": pagination.pages,
        }
        return json_data
    except Exception as e:
        raise e


def fetch_performed_task(pt_id_key):
    """
    Fetches a Performed task from the database based on either its ID or key.

    Parameters:
    - pt_id_key (int or str): The ID or task_key of the task to fetch. 
        - If an integer, the function fetches the task by ID; 
        - if a string, it fetches the task by task_key.

    Returns:
    - Task or None: The fetched Performed task if found, or None if no Performed task matches the provided ID or key.
    """
    try:
        # Check if task_id_key is an integer
        pt_id_key = int(pt_id_key)
        # Fetch the task by id
        performed_task = TaskPerformance.query.filter_by(id=pt_id_key).first()
    except ValueError:
        # If not an integer, treat it as a string
        performed_task = TaskPerformance.query.filter_by(key=pt_id_key).first()

    if performed_task:
        return performed_task
    else:
        return None
