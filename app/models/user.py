'''
This module defines the User model for the database.

It includes fields for the user's email, password, and other necessary information,
as well as methods for password hashing and verification.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''

from sqlalchemy.orm import backref
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db
from ..models import Media
from ..models.role import Role
from ..models.payment import TransactionType
from enum import Enum
from config import Config

# temporary user
class TempUser(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ID: {self.id}, email: {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'date_joined': self.date_joined,
        }

# Define the User data model.
class Trendit3User(db.Model):
    __tablename__ = "trendit3_user"
    
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    thePassword = db.Column(db.String(255), nullable=True)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    two_fa_secret = db.Column(db.String(255), nullable=True)

    # Relationships
    social_ids = db.relationship('SocialIDs', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    social_links = db.relationship('SocialLinks', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    profile = db.relationship('Profile', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    address = db.relationship('Address', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    membership = db.relationship('Membership', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    wallet = db.relationship('Wallet', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    otp_token = db.relationship('OneTimeToken', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'), cascade="all, delete-orphan", single_parent=True)
    user_settings = db.relationship('UserSettings', back_populates='trendit3_user', uselist=False, cascade='all, delete-orphan')
    
    # notifications = db.relationship('Notification', secondary='user_notification', backref=db.backref('users', lazy='dynamic'))
    notifications = db.relationship('Notification', secondary='user_notification', back_populates="recipients")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.thePassword = generate_password_hash(password)
    
    def verify_password(self, password):
        '''
        #This returns True if the password is same as hashed password in the database.
        '''
        return check_password_hash(self.thePassword, password)
    
    @property
    def full_name(self):
        return f"{self.profile.firstname} {self.profile.lastname}"
    
    @property
    def is_2fa_enabled(self):
        return self.user_settings.is_2fa_enabled if self.user_settings else False
    
    def two_fa_info(self):
        return {
                'enabled': self.is_2fa_enabled,
                'method': self.user_settings.two_factor_method if self.user_settings else None,
                }
    
    @property
    def wallet_balance(self):
        return self.wallet.balance
    
    @property
    def role_names(self) -> list[str]:
        """Returns a list of role names for the user."""
        return [str(role.name.value) for role in self.roles]
    
    @property
    def total_tasks(self) -> int:
        """Returns the total number of tasks for the user."""
        return self.tasks.count()
    
    @property
    def total_advert_tasks(self) -> int:
        """Returns the total number of advert tasks for the user."""
        return self.tasks.filter_by(task_type="advert").count()
    
    @property
    def total_engagement_tasks(self) -> int:
        """Returns the total number of engagement tasks for the user."""
        return self.tasks.filter_by(task_type="engagement").count()
    
    @property
    def total_performed_tasks(self) -> int:
        """Returns the total number of performed tasks for the user."""
        return self.performed_tasks.count()
    
    @property
    def task_metrics(self) -> dict:
        return {
            'total_tasks': self.total_tasks,
            'total_advert_tasks': self.total_advert_tasks,
            'total_engagement_tasks': self.total_engagement_tasks,
            'total_performed_tasks': self.total_performed_tasks,
        }
    
    @property
    def total_credited(self) -> float:
        """Returns the total amount ever credited to the user."""
        return self.transactions.filter_by(transaction_type=TransactionType.CREDIT).sum('amount')

    @property
    def total_debited(self) -> float:
        """Returns the total amount ever debited from the user."""
        return self.transactions.filter_by(transaction_type=TransactionType.DEBIT).sum('amount')
    
    @property
    def total_withdrawal(self) -> float:
        """Returns the total amount ever debited from the user."""
        return self.transactions.filter_by(transaction_type=TransactionType.WITHDRAWAL).sum('amount')
    
    @property
    def transaction_metrics(self) -> dict:
        return {
            'total_credited': self.total_credited,
            'total_debited': self.total_debited,
            'total_withdrawal': self.total_withdrawal
        }
    
    @property
    def is_membership_paid(self) -> bool:
        return self.membership.membership_fee_paid
    
    def __repr__(self):
        return f'<ID: {self.id}, username: {self.username}, email: {self.email}>'
    
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def membership_fee(self, paid: bool) -> None:
        if not isinstance(paid, bool):
            raise TypeError("paid must be a boolean")
        
        self.membership.membership_fee_paid = paid
        db.session.commit()
    
    def to_dict(self) -> dict:
        
        address_info = {}
        if self.address:
            address_info = self.address.to_dict()
            address_info.pop("id")
        
        profile_data = {}
        if self.profile:
            profile_data = self.profile.to_dict()
            profile_data.pop("id")
        
        bank_details = {}
        primary_bank = BankAccount.query.filter_by(trendit3_user_id=self.id, is_primary=True).first()
        if primary_bank:
            bank_details.update(primary_bank.to_dict())
        
        user_wallet = self.wallet.to_dict()
        user_wallet.pop("id")
        wallet_info = user_wallet
        
        user_social_profiles = self.social_media_profiles
        social_profiles = [social_profile.to_dict() for social_profile in user_social_profiles]
        
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_joined': self.date_joined,
            'membership_fee': self.membership.membership_fee_paid,
            'wallet': wallet_info,
            'social_profiles': social_profiles,
            'primary_bank': bank_details,
            'roles': self.role_names,
            'two_fa': self.two_fa_info(),
            **address_info,  # Merge address information into the output dictionary
            **profile_data # Merge profile information into the output dictionary
        }



class Profile(db.Model):
    __tablename__ = "profile"
    
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(200), nullable=True)
    lastname = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    profile_picture_id = db.Column(db.Integer(), db.ForeignKey('media.id'), nullable=True)
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    
    trendit3_user = db.relationship('Trendit3User', back_populates="profile")
    profile_picture = db.relationship('Media', backref='profile_picture')
    
    def __repr__(self):
        return f'<profile ID: {self.id}, name: {self.firstname}>'
    
    @property
    def referral_link(self):
        return f'{Config.DOMAIN_NAME}/signup/{self.trendit3_user.username}'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    @property
    def profile_pic(self):
        if self.profile_picture_id:
            theImage = Media.query.get(self.profile_picture_id)
            if theImage:
                return theImage.get_path()
            else:
                return ''
        else:
            return ''
        
    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'gender': self.gender,
            'phone': self.phone,
            'birthday': self.birthday,
            'profile_picture': self.profile_pic,
            'referral_link': f'{self.referral_link}' if self.trendit3_user.is_membership_paid else "",
        }


class Address(db.Model):
    __tablename__ = "address"
    
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    local_government = db.Column(db.String(100), nullable=True)
    currency_code = db.Column(db.String(50), nullable=True)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', back_populates="address")
    
    def __repr__(self):
        return f'<address ID: {self.id}, country: {self.country}, LGA: {self.local_government}, person ID: {self.trendit3_user_id}>'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'state': self.state,
            'local_government': self.local_government,
        }


class OneTimeToken(db.Model):
    __tablename__ = "one_time_token"
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)

    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'))
    trendit3_user = db.relationship('Trendit3User', back_populates="otp_token")
    
    def __repr__(self):
        return f'<ID: {self.id}, user ID: {self.trendit3_user_id}, code: ******, used: {self.used}>'
    
    @classmethod
    def create_token(cls, token, trendit3_user_id):
        token = cls(token=token, trendit3_user_id=trendit3_user_id)
        
        db.session.add(token)
        db.session.commit()
        return token
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'created_at': self.created_at,
            'used': self.used,
            'user_id': self.trendit3_user_id,
        }


class ReferralHistory(db.Model):
    __tablename__ = "referral_history"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(900), nullable=True, unique=True)
    status = db.Column(db.String(900), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('referrals', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ID: {self.id}, user ID: {self.trendit3_user_id}, referred_username: {self.username}, status: {self.status}>'

    @classmethod
    def create_referral_history(cls, username, status, trendit3_user, date_joined=datetime.utcnow):
        referral_history = cls(username=username, status=status, date_joined=date_joined, trendit3_user=trendit3_user)
        
        db.session.add(referral_history)
        db.session.commit()
        return referral_history
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'status': self.status,
            'referrer_id': self.trendit3_user_id,
            'date': self.date_joined,
        }


class BankAccount(db.Model):
    __tablename__ = 'bank_account'

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(80), nullable=False)
    bank_code = db.Column(db.Integer, nullable=False)
    account_no = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(250), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    
    # Relationships
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey("trendit3_user.id"), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('bank_accounts', lazy='dynamic'))
    recipient = db.relationship('Recipient', back_populates="bank_account", uselist=False, cascade="all, delete-orphan")
    
    
    def __repr__(self):
        return f'<ID: {self.id}, bank_name: {self.bank_name}, account_no: {self.account_no}, is_primary: {self.is_primary}>'
    
    
    @classmethod
    def add_bank(cls, trendit3_user, bank_name, bank_code, account_no, is_primary=False, **kwargs):
        bank = cls(trendit3_user=trendit3_user, bank_name=bank_name, bank_code=bank_code, account_no=account_no, is_primary=is_primary)
        
        for key, value in kwargs.items():
            setattr(bank, key, value)
        
        db.session.add(bank)
        db.session.commit()
        return bank
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def to_dict(self, user=False):
        user_info = {'user': self.trendit3_user.to_dict(),} if user else {'user_id': self.trendit3_user_id} # optionally include user info in dict
        return {
            'bank_name': self.bank_name,
            'bank_code': self.bank_code,
            'account_no': self.account_no,
            'account_name': self.account_name,
            'is_primary': self.is_primary,
            **user_info,
        }


class Recipient(db.Model):
    __tablename__ = "recipient"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    recipient_code = db.Column(db.String(255), nullable=False, unique=True)
    recipient_id = db.Column(db.Integer, nullable=False)
    recipient_type = db.Column(db.String(), nullable=False, unique=True)

    # Relationships
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey("trendit3_user.id"), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('recipients', lazy='dynamic'))
    
    bank_account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id', ondelete='CASCADE'), nullable=False,)
    bank_account = db.relationship('BankAccount', back_populates="recipient")
    
    
    
    def __repr__(self):
        return f'< ID: {self.id}, name: {self.name}, recipient_code: {self.recipient_code} >'
    
    @classmethod
    def create_recipient(cls, trendit3_user, name, recipient_code, recipient_id, recipient_type, bank_account):
        recipient = cls(trendit3_user=trendit3_user, name=name, recipient_code=recipient_code, recipient_id=recipient_id, recipient_type=recipient_type, bank_account=bank_account)
        
        db.session.add(recipient)
        db.session.commit()
        return recipient
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def to_dict(self, user=False):
        user_info = {'user': self.trendit3_user.to_dict(),} if user else {'user_id': self.trendit3_user_id} # optionally include user info in dict
        return {
            'id': self.id,
            'recipient_code': self.recipient_code,
            'recipient_id': self.recipient_id,
            **user_info,
        }

