import logging
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db

from ...models.notification import MessageStatus, MessageType, UserMessageStatus, Notification, SocialVerification, SocialVerificationStatus
from ...models.user import Trendit3User

from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.user_helpers import get_notifications, mark_as_read
from ...utils.helpers.response_helpers import *

class NotificationController:
    @staticmethod
    def get_user_notifications():
        
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
    def get_user_messages():
        
        try:
            current_user_id = get_jwt_identity()
            message = get_notifications(current_user_id, MessageType.MESSAGE)
            extra_data = {'user_notification': message}
            return success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while getting user messages: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user messages.")
            status_code = 500
            return error_response(msg, status_code)


    @staticmethod
    def get_user_activities():
        
        try:
            current_user_id = get_jwt_identity()
            message = get_notifications(current_user_id, MessageType.ACTIVITY)
            extra_data = {'user_notification': message}
            return success_response('User messages fetched successfully', 200, extra_data)
        
        except Exception as e:
            msg = f'An error occurred while getting user messages: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user messages.")
            status_code = 500
            return error_response(msg, status_code)
        

    @staticmethod
    def broadcast_message(body):
        """
        By default, this function sends the message to all users.

        Returns:
        Notification: The sent notification object.
        """
        try:
            sender_id = int(get_jwt_identity())
            recipients = Trendit3User.query.all()
            Notification.send_notification(
                sender_id=sender_id,
                recipients=recipients,
                body=body,
                message_type=MessageType.MESSAGE
            )
            
            db.session.commit()
            
            msg = f'Notification sent successfully'
            status_code = 200
            return success_response(msg, status_code)

        except Exception as e:
            msg = f'Error sending broadcast message'
            status_code = 500
            logging.exception(f"An exception occurred trying to send broadcast message: ==>", str(e))

            return error_response(msg, status_code)
        
    @staticmethod
    def create_user_notification(body):
        """
        This function creates a notification for events such as login, earning, ads approved.

        Returns:
        Notification: The sent notification object.
        """
        try:
            sender_id = int(get_jwt_identity())
            recipients = Trendit3User.query.filter_by(id=sender_id).first()
            Notification.send_notification(
                sender_id=sender_id,
                recipients=recipients,
                body=body,
                message_type=MessageType.NOTIFICATION
            )

            db.session.commit()
            
            msg = f'Notification sent successfully'
            status_code = 200
            return success_response(msg, status_code)

        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            return error_response('Error connecting to the database.', 500)
        except Exception as e:
            log_exception(f"An exception occurred trying to send broadcast message", e)
            return error_response('An unexpected error. Our developers are already looking into it.', 500)

        
    @staticmethod
    def create_user_activity(body):
        """
        This function is used to create earning activities.

        Returns:
        Notification: The sent notification object.
        """
        try:
            sender_id = int(get_jwt_identity())
            recipients = Trendit3User.query.filter_by(id=sender_id).first()
            Notification.send_notification(
                sender_id=sender_id,
                recipients=recipients,
                body=body,
                message_type=MessageType.ACTIVITY
            )

            db.session.commit()
            
            msg = f'Notification sent successfully'
            status_code = 200
            return success_response(msg, status_code)

        
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            return error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An exception occurred trying to send broadcast message", e)
            return error_response('An unexpected error. Our developers are already looking into it.', 500)
        
    @staticmethod
    def global_search():

        try:
            # user_id = int(get_jwt_identity())
            data = request.get_json()
            query = data["query"]

            if not query:
                return error_response('No search query', 400)
            
            results = Notification.query.filter(Notification.type == MessageType.ACTIVITY).filter(Notification.body.ilike(f'%{query}%')).all()
            
            extra_data = {"search_result": [result.to_dict() for result in results]}

            return success_response("Search successful", 200, extra_data)
        
        except Exception as e:
            msg = f'Error getting search results'
            status_code = 500
            logging.exception(f"An exception occurred trying to fetch search results: ==>", str(e))

            return error_response(msg, status_code)
        
    
    