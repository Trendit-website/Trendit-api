"""
Author: @al-chris

Description: This module contains models and functions for notifications.
"""
from datetime import datetime
from sqlalchemy.orm import backref
from enum import Enum
from flask import request

from app.extensions import db
from app.utils.helpers.basic_helpers import generate_random_string

from app.decorators.auth import roles_required
from app.models.user import Trendit3User



class MessageStatus(Enum):
    READ = 'read'
    UNREAD = 'unread'

class MessageType(Enum):
    MESSAGE = 'message'
    NOTIFICATION = 'notification'
    ACTIVITY = 'activity'

class SocialVerificationStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

user_notification = db.Table(
    'user_notification', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('trendit3_user.id')),
    db.Column('notification_id', db.Integer, db.ForeignKey('notification.id')),
    db.Column('status', db.Enum(MessageStatus), nullable=False, default=MessageStatus.UNREAD)
)

class UserMessageStatus(db.Model):
    """UserMessageStatus model representing the status of messages for each user."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete="CASCADE"), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('notification.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.Enum(MessageStatus), nullable=False, default=MessageStatus.UNREAD)



# Notification model
class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    type = db.Column(db.Enum(MessageType), nullable=False, default=MessageType.MESSAGE)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=True, default=None)
    body = db.Column(db.Text, nullable=True, default=None)

    # Relationships
    # recipients = db.relationship('Trendit3User', secondary=user_notification, backref='received_messages', lazy='dynamic')
    recipients = db.relationship('Trendit3User', secondary=user_notification, back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id}>'

    @classmethod
    def send_notification(cls, sender_id, recipients, body, message_type=MessageType.NOTIFICATION):
        """
        Send a notification from an admin to multiple recipients.

        Args:
            admin (User): The admin user sending the notification.
            recipients (list of User): List of recipient users.
            body (str): Body of the notification message.
            message_type (MessageType): Type of the notification message.
        """
        message = cls(sender_id=sender_id, body=body, type=message_type, recipients=recipients)
        db.session.add(message)
        db.session.flush()  # Ensure the message is added to the session before creating user message statuses
        user_message_statuses = [UserMessageStatus(user_id=recipient.id, message_id=message.id, status=MessageStatus.UNREAD) for recipient in recipients]
        db.session.bulk_save_objects(user_message_statuses)
        db.session.commit()

        return message
        

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'created_at': self.createdAt,
            'updated_at': self.updatedAt,
            'body': self.body
        }
    

# Admin  Notification model
class SocialVerification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    type = db.Column(db.String(25), nullable=False)
    status = db.Column(db.Enum(MessageType), nullable=False, default=MessageType.MESSAGE)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=True, default=None)
    body = db.Column(db.Text, nullable=True, default=None)

    # Relationships
    # recipients = db.relationship('Trendit3User', secondary=user_notification, backref='received_messages', lazy='dynamic')
    # recipients = db.relationship('Trendit3User', secondary=user_notification, back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id}>'
    
    @classmethod
    def send_notification(cls, sender_id, body, status=SocialVerificationStatus.PENDING):
        """
        Send a notification from an admin to multiple recipients.

        Args:
            admin (User): The admin user sending the notification.
            recipients (list of User): List of recipient users.
            body (str): Body of the notification message.
            message_type (MessageType): Type of the notification message.
        """
        message = cls(sender_id=sender_id, body=body, status=status)
        db.session.add(message)
        db.session.commit()

        return message
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status.value,
            'type': self.type,
            'created_at': self.createdAt,
            'updated_at': self.updatedAt,
            'body': self.body
        }