import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import TempUser, Trendit3User
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
        
    
    @staticmethod
    def get_user_by_email():
        try:
            data = request.get_json()
            email = data.get("email")
            # user = Trendit3User.query.get(email)
            user = Trendit3User.query.filter_by(email=email).first()
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
        
    @staticmethod
    def delete_user(user_id: int):
        try:
            user = Trendit3User.query.get(user_id)
            if user is None:
                return error_response('User not found', 404)
            db.session.delete(user)
            db.session.commit()
            db.session.close()
            return success_response('User deleted successfully', 202)
        
        except Exception as e:
            db.session.rollback()
            db.session.close()
            logging.exception("An exception occurred trying to delete user:\n", str(e))
            return error_response('Error deleting user', 500)
        
    
    @staticmethod
    def get_user_task_metrics(user_id: int):
        try:
            user = Trendit3User.query.get(user_id)
            if user is None:
                return error_response('User not found', 404)
            
            task_metrics = user.task_metrics
            extra_data = {
                'task_metrics': task_metrics
            }
            return success_response('User task metrics fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get user task metrics:\n", str(e))
            return error_response('Error getting user task metrics', 500)

        
    @staticmethod
    def get_user_transaction_metrics(user_id: int):
        try:
            user = Trendit3User.query.get(user_id)
            if user is None:
                return error_response('User not found', 404)
            
            transaction_metrics = user.transaction_metrics
            extra_data = {
                'transaction_metrics': transaction_metrics
            }
            return success_response('User transaction metrics fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception("An exception occurred trying to get user transaction metrics:\n", str(e))
            return error_response('Error getting user transaction metrics', 500)