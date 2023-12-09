import sys, logging
from flask import request, jsonify, current_app
from sqlalchemy import or_
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import Task, AdvertTask, EngagementTask, TaskPerformance
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.utils.helpers.media_helpers import save_media


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
            tasks = AdvertTask.query.filter_by(payment_status='Complete').all()
        elif task_type == 'engagement':
            tasks = EngagementTask.query.filter_by(payment_status='Complete').all()
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
        media =  request.files['media']
        
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
                task.update(trendit3_user_id=user_id, type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, posts_count=posts_count, target_country=target_country, target_state=target_state, gender=gender, caption=caption, hashtags=hashtags)
                
                return task
            else:
                new_task = AdvertTask.create_task(trendit3_user_id=user_id, type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, posts_count=posts_count, target_country=target_country, target_state=target_state, gender=gender, caption=caption, hashtags=hashtags)
                
                return new_task
            
        elif task_type == 'engagement':
            if task:
                task.update(trendit3_user_id=user_id, type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, goal=goal, account_link=account_link, engagements_count=engagements_count)
                
                return task
            else:
                new_task = EngagementTask.create_task(trendit3_user_id=user_id, type=task_type, platform=platform, fee=fee, media_id=media_id, payment_status=payment_status, goal=goal, account_link=account_link, engagements_count=engagements_count)
                
                return new_task
        else:
            return None
    except Exception as e:
        logging.exception(f"An exception occurred trying to save Task {data.get('task_type')}:\n", str(e))
        db.session.rollback()
        console_log('sys excInfo', sys.exc_info())
        return None


def save_performed_task(data, pt_id=None, status='Pending'):
    try:
        user_id = int(get_jwt_identity())
        
        task_id_key = data.get('task_id_key', '')
        task = fetch_task(task_id_key)
        if task is None:
            raise ValueError("Task not found.")
        
        task_id = task.id
        
        reward_money = float(data.get('reward_money'))
        screenshot = request.files['screenshot']
        
        
        task_type = task.type
        
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
            new_performed_task = TaskPerformance.create_task_performance(user_id=user_id, task_id=task_id, task_type=task_type, reward_money=reward_money, proof_screenshot_id=screenshot_id, status=status)
            
            return new_performed_task
    except Exception as e:
        logging.exception("An exception occurred trying to save performed task:\n", str(e))
        db.session.rollback()
        raise e


def fetch_performed_task(pt_id_key):
    """
    Fetches a performed task from the database based on either its ID or key.

    Parameters:
    - pt_id_key (int or str): The ID or key of the task to fetch. 
        - If an integer, the function fetches the performed task by ID; 
        - if a string, it fetches the performed task by key.

    Returns:
    - TaskPerformance or None: The fetched performed task if found, or None if no performed task matches the provided ID or key.
    """
    try:
        # Check if task_id_key is an integer
        task_id_key = int(task_id_key)
        # Fetch the task by id
        performed_task = TaskPerformance.query.filter_by(id=task_id_key).first()
    except ValueError:
        # If not an integer, treat it as a string
        performed_task = TaskPerformance.query.filter_by(key=task_id_key).first()

    if performed_task:
        return performed_task
    else:
        return None
