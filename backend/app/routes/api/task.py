from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api import TaskController


# ALL TASKS
@api.route('/current-user/tasks', methods=['GET'])
@jwt_required()
def get_current_user_tasks():
    return TaskController.get_current_user_tasks()

@api.route('/tasks', methods=['GET'])
def get_all_tasks():
    return TaskController.get_tasks()

@api.route('/tasks/counts/<field>', methods=['GET'])
def get_all_aggregated_task_counts(field):
    return TaskController.get_all_aggregated_task_counts(field)

@api.route('/tasks/<task_id_key>', methods=['GET'])
def get_single_task(task_id_key):
    return TaskController.get_single_task(task_id_key)


# ADVERT TASKS
@api.route('/tasks/advert', methods=['GET'])
def get_all_advert_tasks():
    return TaskController.get_advert_tasks()

@api.route('/tasks/advert/<platform>', methods=['GET'])
def get_advert_tasks_by_platform(platform):
    return TaskController.get_advert_tasks_by_platform(platform.lower())

@api.route('/tasks/advert/grouped-by/<field>', methods=['GET'])
def get_advert_tasks_grouped_by_field(field):
    return TaskController.get_advert_tasks_grouped_by_field(field)

@api.route('/tasks/advert/counts/<field>', methods=['GET'])
def get_advert_aggregated_task_counts(field):
    return TaskController.get_advert_aggregated_task_counts(field)



# ENGAGEMENT TASKS
@api.route('/tasks/engagement', methods=['GET'])
def get_all_engagement_tasks():
    return TaskController.get_engagement_tasks()

@api.route('/tasks/engagement/grouped-by/<field>', methods=['GET'])
def get_engagement_tasks_grouped_by_field(field):
    return TaskController.get_engagement_tasks_grouped_by_field(field)

@api.route('/tasks/engagement/counts/<field>', methods=['GET'])
def get_engagement_aggregated_task_counts(field):
    return TaskController.get_engagement_aggregated_task_counts(field)


# CREATE NEW TASK
@api.route('/tasks/new', methods=['POST'])
@jwt_required()
def create_task():
    return TaskController.create_task()

