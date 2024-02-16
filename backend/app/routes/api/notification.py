from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api import NotificationController


@api.route('/notifications', methods=['POST'])
@jwt_required()
def get_user_notifications():
    return NotificationController.get_notifications()


@api.route('/messages', methods=['POST'])
@jwt_required()
def get_user_messages():
    return NotificationController.get_messages()


@api.route('/activities', methods=['POST'])
@jwt_required()
def get_user_activities():
    return NotificationController.get_activities()