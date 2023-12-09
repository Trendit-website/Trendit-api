from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api import TaskController


@bp.route('/current-user/tasks', methods=['GET'])
@jwt_required()
def get_current_user_tasks():
    return TaskController.get_current_user_tasks()

@bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    return TaskController.get_tasks()

@bp.route('/tasks/<task_id_key>', methods=['GET'])
def get_single_task(task_id_key):
    return TaskController.get_single_task(task_id_key)

@bp.route('/tasks/advert', methods=['GET'])
def get_all_advert_tasks():
    return TaskController.get_advert_tasks()


@bp.route('/tasks/engagement', methods=['GET'])
def get_all_engagement_tasks():
    return TaskController.get_engagement_tasks()


@bp.route('/tasks/advert/grouped-by/<field>', methods=['GET'])
def get_advert_tasks_grouped_by_field(field):
    return TaskController.get_advert_tasks_grouped_by_field(field)


@bp.route('/tasks/advert/<platform>', methods=['GET'])
def get_advert_tasks_by_platform(platform):
    return TaskController.get_advert_tasks_by_platform(platform.lower())


@bp.route('/tasks/engagement/grouped-by/<field>', methods=['GET'])
def get_engagement_tasks_grouped_by_field(field):
    return TaskController.get_engagement_tasks_grouped_by_field(field)


@bp.route('/tasks/new', methods=['POST'])
@jwt_required()
def create_task():
    return TaskController.create_task()