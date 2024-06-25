'''
This module defines the settings model for the database.


@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''

from ..extensions import db


notification_type = ['EMAIL', 'IN_APP', 'PUSH']
notification_subtype = ['NEW_FEATURES', 'NEW_TASKS', 'MONEY_EARNED']

class UserSettings(db.Model):
    __tablename__ = 'user_settings'

    id = db.Column(db.Integer, primary_key=True)

    # Relationship with Trendit3User
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', back_populates='user_settings')

    # Inherit fields and relationships from other models
    notification_preference = db.relationship('NotificationPreference', back_populates="user_settings", uselist=False, cascade="all, delete-orphan")
    user_preference = db.relationship('UserPreference', back_populates="user_settings", uselist=False, cascade="all, delete-orphan")
    security_setting = db.relationship('SecuritySetting', back_populates="user_settings", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ID: {self.id}, user_id: {self.trendit3_user_id} >'
    
    @property
    def is_2fa_enabled(self):
        two_factor_method = self.security_setting.two_factor_method if self.security_setting else None
        if two_factor_method is None:
            return False
        
        return True
    
    @property
    def two_factor_method(self):
        return self.security_setting.two_factor_method if self.security_setting else None
    
    @classmethod
    def create_user_settings(cls, trendit3_user_id):
        default_settings = cls(trendit3_user_id=trendit3_user_id)
        
        db.session.add(default_settings)
        db.session.commit()
        
        return default_settings
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class NotificationPreference(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email_new_features = db.Column(db.Boolean, default=False)
    email_new_tasks = db.Column(db.Boolean, default=False)
    email_money_earned = db.Column(db.Boolean, default=True)
    
    in_app_new_features = db.Column(db.Boolean, default=False)
    in_app_new_tasks = db.Column(db.Boolean, default=False)
    in_app_money_earned = db.Column(db.Boolean, default=True)
    
    push_new_features = db.Column(db.Boolean, default=False)
    push_new_tasks = db.Column(db.Boolean, default=False)
    push_money_earned = db.Column(db.Boolean, default=True)
    
    user_settings_id = db.Column(db.Integer, db.ForeignKey('user_settings.id', ondelete='CASCADE'), nullable=False,)
    user_settings = db.relationship('UserSettings', back_populates="notification_preference")


    def __repr__(self):
        return f'<ID: {self.id} >'
    
    @property
    def total_notifications_enabled(self):
        return sum([getattr(self, attr) for attr in self.__dict__ if isinstance(getattr(self, attr), bool)])
    
    @property
    def total_notifications_disabled(self):
        return sum([not getattr(self, attr) for attr in self.__dict__ if isinstance(getattr(self, attr), bool)])
    
    def reset_notification_settings(self):
        for attr in self.__dict__:
            if isinstance(getattr(self, attr), bool):
                setattr(self, attr, False)  # Reset all boolean attributes to False
    
    
    def is_notification_enabled(self, notification_name):
        """
        Check if a specific notification type/subtype is enabled.
        
        Args:
            notification_name (str): The notification name (e.g., 'email_new_features', 'in_app_money_earned').
        
        Returns:
            bool: True if the notification is enabled, False otherwise.
        """
        return getattr(self, notification_name, False)
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'email_new_features': self.email_new_features,
            'email_new_tasks': self.email_new_tasks,
            'email_money_earned': self.email_money_earned,
            'in_app_new_features': self.in_app_new_features,
            'in_app_new_tasks': self.in_app_new_tasks,
            'in_app_money_earned': self.in_app_money_earned,
            'push_new_features': self.push_new_features,
            'push_new_tasks': self.push_new_tasks,
            'push_money_earned': self.push_money_earned,
            'total_enabled': self.total_notifications_enabled,
            'total_disabled': self.total_notifications_disabled
        }


class UserPreference(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    appearance = db.Column(db.String(150), default='light', nullable=False) # 'light', 'dark', or 'system'
    
    user_settings_id = db.Column(db.Integer, db.ForeignKey('user_settings.id', ondelete='CASCADE'), nullable=False,)
    user_settings = db.relationship('UserSettings', back_populates="user_preference")


    def __repr__(self):
        return f'<ID: {self.id}, appearance: {self.appearance} >'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def update_appearance(self, new_appearance):
        """
        Update the appearance preference for a user.
        """
        self.appearance = new_appearance

    @staticmethod
    def validate_appearance(appearance):
        """
        Validate the appearance preference against allowed values.
        """
        allowed_values = ['light', 'dark', 'system']
        return appearance in allowed_values
    
    def to_dict(self):
        return {
            'appearance': self.appearance,
        }


class SecuritySetting(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    two_factor_method = db.Column(db.String(150), nullable=True) # either email, phone or google_auth_app.
    
    user_settings_id = db.Column(db.Integer, db.ForeignKey('user_settings.id', ondelete='CASCADE'), nullable=False,)
    user_settings = db.relationship('UserSettings', back_populates="security_setting")


    def __repr__(self):
        return f'<ID: {self.id}, 2FA_method: {self.two_factor_method}>'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    
    def update_2fa_method(self, new_method):
        """
        Update the 2FA method for a user.
        """
        self.two_factor_method = new_method

    @staticmethod
    def validate_2fa_method(method):
        """
        Validate the 2FA method against allowed values.
        """
        allowed_values = ['email', 'phone', 'google_auth_app', None]
        return method in allowed_values
    
    def to_dict(self):
        return {
            'two_fa_method': self.two_factor_method,
        }