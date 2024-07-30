from flask_jwt_extended import jwt_required
from flask import request

from . import api
from app.controllers.api import NotificationController


@api.route('/notifications', methods=["GET", "POST"])
@jwt_required()
def get_user_notifications():
    return NotificationController.get_user_notifications()

@api.route('/notifications/<notification_id>', methods=["PATCH"])
@jwt_required()
def mark_notification_read(notification_id):
    return NotificationController.mark_notification_read(notification_id)


@api.route('/messages', methods=["POST"])
@jwt_required()
def get_user_messages():
    return NotificationController.get_user_messages()


@api.route('/activities', methods=["POST"])
@jwt_required()
def get_user_activities():
    return NotificationController.get_user_activities()


@api.route('/broadcast_message', methods=['POST'])
@jwt_required()
def broadcast_message():
    data = request.get_json()
    message = data.get('message')
    return NotificationController.broadcast_message(message)


@api.route('/global_search', methods=["POST"])
@jwt_required()
def global_search():
    return NotificationController.global_search()