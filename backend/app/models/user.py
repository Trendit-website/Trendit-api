from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    address = db.relationship('Address', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    membership = db.relationship('Membership', back_populates="trendit3_user", uselist=False, cascade="all, delete-orphan")
    
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

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'date_joined': self.date_joined
        }

class Address(db.Model):
    __tablename__ = "address"
    
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    local_government = db.Column(db.String(100), nullable=False)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', back_populates="address")
    
    def __repr__(self):
        return f'<address ID: {self.id}, country: {self.country}, LGA: {self.local_government}, person ID: {self.trendit3_user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'state': self.state,
            'local_government': self.local_government,
            'trendit3_user_id': self.trendit3_user_id
        }
