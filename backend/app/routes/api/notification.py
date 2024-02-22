from flask_jwt_extended import jwt_required
from flask import request

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

api.route('/broadcast_message', methods=['POST'])
@jwt_required()
def broadcast_message():
    message = request.get_json("message")
    return NotificationController.send_notification(message)