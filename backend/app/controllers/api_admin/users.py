import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import TempUser, Trendit3User
from app.utils.helpers.task_helpers import save_performed_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log


class AdminUsers:
    @staticmethod
    def get_all_users():
        try:
            users = Trendit3User.query.all()
            user_list = []
            for user in users:
                user_list.append(user.to_dict())
            extra_data = {
                'total': len(user_list),
                'users': user_list
            }

            return success_response('All users fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get all users:\n", str(e))
            return error_response('Error getting all users', 500)
        
    
    @staticmethod
    def get_user(user_id: int):
        try:
            user = Trendit3User.query.get(user_id)
            if user is None:
                return error_response('User not found', 404)
            user_dict = user.to_dict()
            extra_data = {
                'user': user_dict
            }
            return success_response('User fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get user:\n", str(e))
            return error_response('Error getting user', 500)