from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api import TaskController


@bp.route('/tasks', methods=['GET'])
def get_all_tasks():
    return TaskController.get_tasks()


@bp.route('/tasks/advert', methods=['GET'])
def get_all_advert_tasks():
    return TaskController.get_advert_tasks()


@bp.route('/tasks/engagement', methods=['GET'])
def get_all_engagement_tasks():
    return TaskController.get_engagement_tasks()


@bp.route('/tasks/new', methods=['POST'])
@jwt_required(optional=True)
def create_task():
    return TaskController.create_task()
