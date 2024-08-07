from flask import current_app, request
from flask_jwt_extended import jwt_required

from . import api
from ...controllers.api import TaskOptionsController
from ...utils.helpers.response_helpers import success_response

# CREATE NEW TASK
@api.route('/task_options', methods=['GET'])
@jwt_required()
def get_task_options():
    return TaskOptionsController.get_task_options()