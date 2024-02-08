from uuid import uuid4
from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime

from ..utils.helpers.basic_helpers import generate_random_string


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.UUID(as_uuid=True), unique=True, nullable=False, default=uuid4())
    amount = db.Column(db.Float(), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # 'task-creation', 'membership_fee' or 'product_fee'
    payment_method = db.Column(db.String(), nullable=False)  # 'wallet' or 'payment gateway(paystack)'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    user = db.relationship('Trendit3User')
    
    def __repr__(self):
        return f'<ID: {self.id}, Amount: {self.amount}, Payment Method: {self.payment_method}, Payment Type: {self.payment_type}>'
    
    
    @classmethod
    def create_payment_record(cls, key, amount, payment_type, payment_method, trendit3_user_id):
        payment_record = cls(key=generate_random_string(100), amount=amount, payment_type=payment_type, payment_method=payment_method, trendit3_user_id=trendit3_user_id)
        
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
            'created_at': self.created_at
        }


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(80), unique=True, nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    user_id = db.Column(db.String(120), unique=False, nullable=False)
    payment_type = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'withdrawals' or 'payment'
    
    
    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('transactions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ID: {self.id}, Transaction Reference: {self.tx_ref}, Payment Type: {self.payment_type}, Status: {self.status}>'
    
    
    @classmethod
    def create_transaction(cls, trendit3_user, tx_ref, payment_type, status, transaction_type):
        transaction = cls(trendit3_user=trendit3_user, tx_ref=tx_ref, payment_type=payment_type, status=status, transaction_type=transaction_type)
        
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
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
            'tx_ref': self.tx_ref,
            'payment_type': self.payment_type,
            'status': self.status,
            **user_info,
        }


class PaystackTransaction(db.Model):
    __tablename__ = 'paystack_transactions'

    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(120), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('paystack_transactions', lazy='dynamic'))

    def __repr__(self):
        return f'<ID: {self.id}, Transaction Reference: {self.tx_ref}, Payment Type: {self.payment_type}, Status: {self.status}>'
    
    
    @classmethod
    def create_transaction(cls, trendit3_user, tx_ref, payment_type, status, amount):
        transaction = cls(trendit3_user=trendit3_user, tx_ref=tx_ref, payment_type=payment_type, status=status, amount=amount)
        
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
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
            'amount': self.amount,
            'status': self.status,
            'tx_ref': self.tx_ref,
            'payment_type': self.payment_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            **user_info,
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
    
    
    def __repr__(self):
        return f'<ID: {self.id}, Balance: {self.balance}, Currency Name: {self.currency_name}>'
    
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


    def to_dict(self, user=False):
        user_info = {'user': self.trendit3_user.to_dict(),} if user else {'user_id': self.trendit3_user_id} # optionally include user info in dict
        return {
            'id': self.id,
            'balance': self.balance,
            'currency_name': self.currency_name,
            'currency_code': self.currency_code,
            **user_info,
        }




class Withdrawal(db.Model):
    __tablename__ = 'withdrawal'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_no = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'pending' or 'completed'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('withdrawals', lazy='dynamic'))

    def __repr__(self):
        return f'<ID: {self.id}, amount: {self.amount}, account_no: {self.account_no}, Status: {self.status}>'
    
    @classmethod
    def create_withdrawal(cls, trendit3_user, amount, bank_name, account_no, status):
        withdrawal = cls(trendit3_user=trendit3_user, amount=amount, bank_name=bank_name, account_no=account_no, status=status)
        
        db.session.add(withdrawal)
        db.session.commit()
        return withdrawal
    
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
            'amount': self.amount,
            'bank_name': self.bank_name,
            'account_no': self.account_no,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            **user_info,
        }

