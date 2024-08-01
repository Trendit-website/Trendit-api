"""
Author: @al-chris

Description: This module contains models and functions for notifications.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import backref
from enum import Enum

from app.extensions import db



class MessageStatus(Enum):
    READ = 'read'
    UNREAD = 'unread'

class NotificationType(Enum):
    MESSAGE = 'message'
    NOTIFICATION = 'notification'
    ACTIVITY = 'activity'

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
    notification_type = db.Column(db.Enum(NotificationType), nullable=False, default=NotificationType.MESSAGE)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    title = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=True, default=None)
    read = db.Column(db.Boolean, nullable=True, default=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=True)

    # Relationships
    # recipients = db.relationship('Trendit3User', secondary=user_notification, backref='received_messages', lazy='dynamic')
    recipients = db.relationship('Trendit3User', secondary=user_notification, back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id}>'

    @classmethod
    def add_notification(cls, recipient_id, body, notification_type=NotificationType.NOTIFICATION, commit=True):
        """
        Send a notification from an admin to multiple recipients.

        Args:
            admin (User): The admin user sending the notification.
            recipients (list of User): List of recipient users.
            body (str): Body of the notification message.
            notification_type (NotificationType): Type of the notification message.
        """
        message = cls(recipient_id=recipient_id, body=body, notification_type=notification_type)
        db.session.add(message)
        
        if commit:
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
            "type": self.notification_type.value,
            "title": self.title,
            "body": self.body,
            "read": self.read,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    

# Admin  Notification model
class SocialVerification(db.Model):
    __tablename__ = 'social_verification'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    type = db.Column(db.String(25), nullable=False)
    status = db.Column(db.Enum(SocialVerificationStatus), nullable=False, default=SocialVerificationStatus.PENDING)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    updatedAt = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    body = db.Column(db.Text, nullable=True, default=None)

    # Relationships
    # recipients = db.relationship('Trendit3User', secondary=user_notification, backref='received_messages', lazy='dynamic')
    # recipients = db.relationship('Trendit3User', secondary=user_notification, back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id}>'
    
    @classmethod
    def add_notification(cls, sender_id, body, type, status=SocialVerificationStatus.PENDING, commit=True):
        """
        Send a notification from an admin to multiple recipients.

        Args:
            admin (User): The admin user sending the notification.
            recipients (list of User): List of recipient users.
            body (str): Body of the notification message.
            type (str): Type of the notification message.
            notification_type (NotificationType): Type of the notification message.
        """
        message = cls(sender_id=sender_id, body=body, status=status, type=type)
        db.session.add(message)
        
        if commit:
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
            'sender_id': self.sender_id,
            'type': self.type,
            'created_at': self.createdAt,
            'updated_at': self.updatedAt,
            'body': self.body
        }