import logging
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db

from ...models import Notification, NotificationType
from ...models.user import Trendit3User

from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.user_helpers import get_notifications, mark_as_read
from ...utils.helpers.response_helpers import *

class NotificationController:
    @staticmethod
    def get_user_notifications():
        
        try:
            current_user_id = get_jwt_identity()
            page = request.args.get("page", 1, type=int)
            notification_type = request.args.get("type", "")
            tasks_per_page = int(10)
            
            notifications_query: list[Notification] = Notification.query
            
            if notification_type:
                try:
                    type_enum = NotificationType[notification_type.upper()]
                except KeyError:
                    return error_response("Invalid notification type", 400)
                
                notifications_query: list[Notification] = Notification.query.filter(Notification.type==type_enum)
            
            pagination = notifications_query.filter_by(type=type_enum, recipient_id=current_user_id) \
                .order_by(Notification.created_at.desc()) \
                .paginate(page=page, per_page=tasks_per_page, error_out=False)
            
            
            notifications: list[Notification] = pagination.items
            current_notifications = [notification.to_dict() for notification in notifications]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "notifications": current_notifications,
            }
            
            if not notifications:
                return success_response(f'There are no notifications yet', 200, extra_data)
            
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
            message = get_notifications(current_user_id, NotificationType.MESSAGE)
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
            message = get_notifications(current_user_id, NotificationType.ACTIVITY)
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
            recipient_id = int(get_jwt_identity())
            recipients = Trendit3User.query.all()
            Notification.add_notification(
                recipient_id=recipient_id,
                body=body,
                message_type=NotificationType.MESSAGE
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
            recipient_id = int(get_jwt_identity())
            recipients = Trendit3User.query.filter_by(id=recipient_id).first()
            Notification.add_notification(
                recipient_id=recipient_id,
                body=body,
                message_type=NotificationType.NOTIFICATION
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
            recipient_id = int(get_jwt_identity())
            recipients = Trendit3User.query.filter_by(id=recipient_id).first()
            Notification.add_notification(
                recipient_id=recipient_id,
                body=body,
                message_type=NotificationType.ACTIVITY
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
            
            results = Notification.query.filter(Notification.type == NotificationType.ACTIVITY).filter(Notification.body.ilike(f'%{query}%')).all()
            
            extra_data = {"search_result": [result.to_dict() for result in results]}

            return success_response("Search successful", 200, extra_data)
        
        except Exception as e:
            msg = f'Error getting search results'
            status_code = 500
            logging.exception(f"An exception occurred trying to fetch search results: ==>", str(e))

            return error_response(msg, status_code)
        
    
    