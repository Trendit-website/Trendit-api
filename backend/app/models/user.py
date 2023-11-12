from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import Image

# Define the User data model. added flask_login UserMixin!!
class Trendit3User(db.Model):
    __tablename__ = "trendit3_user"
    
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    gender = db.Column(db.String(50), nullable=False)
    thePassword = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    profile = db.relationship('Profile', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    address = db.relationship('Address', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    membership = db.relationship('Membership', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    wallet = db.relationship('Wallet', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    pwd_reset_token = db.relationship('PwdResetToken', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    
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
        
    def marketplace_upload_fee(self, paid: bool) -> None:
        if not isinstance(paid, bool):
            raise TypeError("paid must be a boolean")
        
        self.membership.item_upload_paid = paid
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
            })

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
                'symbol': self.wallet.symbol
            },
            **address_info,  # Merge address information into the output dictionary
            **profile_data # Merge profile information into the output dictionary
        }


class Profile(db.Model):
    __tablename__ = "profile"
    
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(200), nullable=True)
    lastname = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    profile_picture_id = db.Column(db.Integer(), db.ForeignKey('image.id'), nullable=True)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', back_populates="profile")
    
    def __repr__(self):
        return f'<profile ID: {self.id}, name: {self.firstname}>'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def get_profile_img(self):
        if self.profile_picture_id:
            theImage = Image.query.get(self.profile_picture_id)
            if theImage:
                return theImage.get_path("original")
            else:
                return None
        else:
            return None
        
    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'phone': self.phone,
            'profile_picture': self.get_profile_img()
        }


class Address(db.Model):
    __tablename__ = "address"
    
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    local_government = db.Column(db.String(100), nullable=False)
    currency_code = db.Column(db.String(50), nullable=False)
    
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


class PwdResetToken(db.Model):
    __tablename__ = "password_reset_token"
    
    id = db.Column(db.Integer, primary_key=True)
    reset_token = db.Column(db.String(900), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)

    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'))
    trendit3_user = db.relationship('Trendit3User', back_populates="pwd_reset_token")
    
    def __repr__(self):
        return f'<ID: {self.id}, user ID: {self.user_id}, code: ******, used: {self.used}>'
    
    @classmethod
    def create_token(cls, reset_token, trendit3_user_id):
        token = cls(reset_token=reset_token, trendit3_user_id=trendit3_user_id)
        
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
            'code': self.reset_token,
            'created_at': self.created_at,
            'used': self.used,
            'user_id': self.trendit3_user_id,
        }

