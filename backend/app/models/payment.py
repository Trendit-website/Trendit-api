from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # 'task_fee', 'activation_fee' or 'monthly_fee'
    payment_method = db.Column(db.String(), nullable=False)  # 'wallet' or 'payment gateway'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    user = db.relationship('Trendit3User')
    
    def __repr__(self):
        return f'<ID: {self.id}, Amount: {self.amount}, Payment Method: {self.payment_method}, Payment Type: {self.payment_type}>'
    
    
    @classmethod
    def create_payment_record(cls, key, amount, payment_type, payment_method, trendit3_user_id):
        payment_record = cls(key=key, amount=amount, payment_type=payment_type, payment_method=payment_method, trendit3_user_id=trendit3_user_id)
        
        db.session.add(payment_record)
        db.session.commit()
        
        return payment_record
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.trendit3_user_id,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'payment_method': self.payment_method,
            'timestamp': self.timestamp
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.String(120), unique=False, nullable=False)
    payment_type = db.Column(db.String(120), unique=False, nullable=False)
    status = db.Column(db.String(80), unique=False, nullable=False)
    
    
    def __repr__(self):
        return f'<ID: {self.id}, Transaction Reference: {self.tx_ref}, Payment Type: {self.payment_type}, Status: {self.status}>'
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'tx_ref': self.tx_ref,
            'user_id': self.user_id,
            'payment_type': self.payment_type,
            'status': self.status
        }

class Wallet(db.Model):
    __tablename__ = "wallet"

    id = db.Column(db.Integer(), primary_key=True)
    balance = db.Column(db.Float(), default=00.00, nullable=False)
    currency_name = db.Column(db.String(), nullable=False)
    currency_code = db.Column(db.String(), nullable=False)

    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', back_populates="wallet")
    
    @classmethod
    def create_wallet(cls, trendit3_user, balance, currency_name, currency_code, symbol):
        wallet = cls(trendit3_user=trendit3_user, balance=balance, currency_name=currency_name, currency_code=currency_code)
        
        db.session.add(wallet)
        db.session.commit()
        return wallet
    
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
            'user_id': self.trendit3_user_id,
            'balance': self.balance,
            'currency_name': self.currency_name,
            'currency_code': self.currency_code,
        }

