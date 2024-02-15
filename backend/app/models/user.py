'''
This module defines the User model for the database.

It includes fields for the user's email, password, and other necessary information,
as well as methods for password hashing and verification.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''

from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import Media
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

    # Relationships
    profile = db.relationship('Profile', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    address = db.relationship('Address', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    membership = db.relationship('Membership', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    wallet = db.relationship('Wallet', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    otp_token = db.relationship('OneTimeToken', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
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
    def wallet_balance(self):
        return self.wallet.balance
    
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
    
    def activation_fee(self, paid: bool) -> None:
        if not isinstance(paid, bool):
            raise TypeError("paid must be a boolean")
        
        self.membership.activation_fee_paid = paid
        db.session.commit()
        
    def membership_fee(self, paid: bool) -> None:
        if not isinstance(paid, bool):
            raise TypeError("paid must be a boolean")
        
        self.membership.membership_fee_paid = paid
        db.session.commit()
    
    def to_dict(self):
        address_info = {}
        if self.address:
            address_info.update({
                'country': self.address.country,
                'state': self.address.state,
                'local_government': self.address.local_government
            })
        
        profile_data = {}
        if self.profile:
            profile_data.update({
                'firstname': self.profile.firstname,
                'lastname': self.profile.lastname,
                'profile_picture': self.profile.get_profile_img(),
                'referral_link': self.profile.referral_link,
                'referral_code': self.profile.referral_code,
            })
        
        bank_details = {}
        primary_bank = BankAccount.query.filter_by(trendit3_user_id=self.id, is_primary=True).first()
        if primary_bank:
            bank_details.update(primary_bank.to_dict())

        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'date_joined': self.date_joined,
            'wallet': {
                'balance': self.wallet.balance,
                'currency_name': self.wallet.currency_name,
                'currency_code': self.wallet.currency_code,
            },
            'primary_bank': bank_details,
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
    profile_picture_id = db.Column(db.Integer(), db.ForeignKey('media.id'), nullable=True)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', back_populates="profile")
    
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
            'profile_picture': self.profile_pic,
            'referral_link': f'{self.referral_link}',
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
            'currency': self.currency_code,
            'user_id': self.trendit3_user_id
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
    is_primary = db.Column(db.Boolean, default=False)
    
    # Relationships
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey("trendit3_user.id"), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('bank_accounts', lazy='dynamic'))
    recipient = db.relationship('Recipient', back_populates="bank_account", uselist=False, cascade="all, delete-orphan")
    
    
    def __repr__(self):
        return f'<ID: {self.id}, Recipient Code: {self.recipient_code}, is_primary: {self.is_primary}>'
    
    
    @classmethod
    def add_bank(cls, trendit3_user, bank_name, bank_code, account_no, is_primary=False):
        bank = cls(trendit3_user=trendit3_user, bank_name=bank_name, bank_code=bank_code, account_no=account_no, is_primary=is_primary)
        
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
            'id': self.id,
            'bank_code': self.bank_code,
            'bank_name': self.bank_name,
            'account_no': self.account_no,
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
        return f'<ID: {self.id}, Recipient Code: {self.recipient_code}, is_primary: {self.is_primary}>'
    
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

