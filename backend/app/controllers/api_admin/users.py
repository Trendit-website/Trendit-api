import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import TempUser, Trendit3User
from app.utils.helpers.task_helpers import save_performed_task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log


class AdminUsersController:
    @staticmethod
    def get_all_users():
        try:
            page = request.args.get('page', default=1, type=int)
            per_page = request.args.get('per_page', default=10, type=int)
            
            users = Trendit3User.query.paginate(page=page, per_page=per_page, error_out=False)
            
            if page > users.pages:
                return success_response('No content', 204, {'users': []})
            
            user_list = [user.to_dict() for user in users.items]
            
            extra_data = {
                'total': users.total,
                'pages': users.pages,
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