import logging
from flask import request
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTDecodeError

from app.models.notification import MessageStatus, MessageType, UserMessageStatus, Notification
from app.models.user import Trendit3User
from app.utils.helpers.basic_helpers import console_log, log_exception
from app.utils.helpers.user_helpers import get_notifications, mark_as_read
from app.utils.helpers.response_helpers import *

class NotificationController:
    @staticmethod
    def get_notifications():
        
        try:
            current_user_id = get_jwt_identity()
            notification = get_notifications(current_user_id, MessageType.NOTIFICATION)
            extra_data = {'user_notification': notification}
            result = success_response('User notifications fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while getting user notifications: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user notifications.")
            status_code = 500
            result = error_response(msg, status_code)

        finally:
            return result            


    @staticmethod
    def get_messages():
        
        try:
            current_user_id = get_jwt_identity()
            message = get_notifications(current_user_id, MessageType.MESSAGE)
            extra_data = {'user_notification': message}
            result = success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while getting user messages: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user messages.")
            status_code = 500
            result = error_response(msg, status_code)

        finally:
            return result


    @staticmethod
    def get_activities():
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            tasks_per_page = int(6)
            pagination = Notification.query.filter_by(user_id=current_user_id, type=MessageType.ACTIVITY) \
                .order_by(Notification.createdAt.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            
            activities = pagination.items
            current_activities = [activity.to_dict() for activity in activities]
            extra_data = {
                'total': pagination.total,
                "activities": current_activities,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not activities:
                return success_response(f'There are no activities.', 200, extra_data)
            
            msg = f'All activities fetched successfully'
            status_code = 200
            result = success_response(msg, status_code, extra_data)
        
        except Exception as e:
            msg = f'Error getting all activities'
            status_code = 500
            logging.exception(f"An exception occurred trying to get all activities: ==>", str(e))

            result = error_response(msg, status_code)
        
        finally:
            return result
        

    @staticmethod
    def send_notification(body):
        """
        By default, this function sends the message to all users.

        Returns:
        Notification: The sent notification object.
        """
        try:
            sender_id = int(get_jwt_identity())
            recipients = Trendit3User.query.all()
            Notification.send_notification(sender_id=sender_id, recipients=recipients, body=body, message_type=MessageType.MESSAGE)
            
            msg = f'Notification sent successfully'
            status_code = 200
            result = success_response(msg, status_code)

        except Exception as e:
            msg = f'Error sending broadcast message'
            status_code = 500
            logging.exception(f"An exception occurred trying to send broadcast message: ==>", str(e))

            result = error_response(msg, status_code)
        
        finally:
            return result