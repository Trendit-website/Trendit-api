from sqlalchemy.orm import backref
from datetime import datetime
from enum import Enum

from ..extensions import db
from ..utils.helpers.basic_helpers import generate_random_string


class Payment(db.Model):
    """
    Model to represent a payment request made by a user in Trendit³.
    This model captures details about a payment request before it is processed.
    """
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False) # Unique identifier for the payments
    amount = db.Column(db.Float(), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # 'task-creation', 'membership-fee', 'credit-wallet' or 'product-fee'
    payment_method = db.Column(db.String(), nullable=False)  # 'wallet' or 'payment gateway(flutterwave)'
    status = db.Column(db.String(20), nullable=False, default="pending")  # Status of the payment request
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User')
    
    def __repr__(self):
        return f'<ID: {self.id}, Amount: {self.amount}, Payment Method: {self.payment_method}, Payment Type: {self.payment_type}>'
    
    
    @classmethod
    def create_payment_record(cls, key, amount, payment_type, payment_method, status, trendit3_user):
        payment_record = cls(key=key, amount=amount, payment_type=payment_type, payment_method=payment_method, status=status, trendit3_user=trendit3_user)
        
        db.session.add(payment_record)
        db.session.commit()
        
        return payment_record
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self, user=False):
        user_info = {'user': self.trendit3_user.to_dict()} if user else {'user_id': self.trendit3_user_id} # optionally include user info in dict
        return {
            'id': self.id,
            'key': self.key,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'payment_method': self.payment_method,
            'status': self.status,
            'created_at': self.created_at,
            **user_info,
        }


class TransactionType(Enum):
    """ENUMS for the transaction_type filed in Transaction Model"""
    CREDIT = 'credit'
    DEBIT = 'debit'
    PAYMENT = 'payment'
    WITHDRAWAL = 'withdrawal'
    
class Transaction(db.Model):
    """
    Model to represent a financial transaction associated with a payment in Trendit³.
    This model captures details about the financial aspect of a payment or withdrawal.
    """
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False) # Unique identifier for the financial transaction
    amount = db.Column(db.Float(), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)  # 'credit', 'debit', 'payment' or 'withdraw'
    description = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(80), nullable=False) # Status of the financial transaction
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('transactions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ID: {self.id}, Transaction Reference: {self.key}, Transaction Type: {self.transaction_type}, Status: {self.status}>'
    
    
    @classmethod
    def create_transaction(cls, key, amount, transaction_type, description, status, trendit3_user):
        transaction = cls(key=key, amount=amount, transaction_type=transaction_type, description=description, status=status, trendit3_user=trendit3_user)
        
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
            'key': self.key,
            'amount': self.amount,
            'transaction_type': str(self.transaction_type.value),
            'description': self.description,
            'status': self.status,
            **user_info,
        }


class Withdrawal(db.Model):
    """
    Model to represent a withdrawal request made by a user in Trendit³.
    This model captures details about a withdrawal request before it is processed.
    """
    __tablename__ = 'withdrawal'

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), nullable=False) # Unique reference for the withdrawal request
    amount = db.Column(db.Float, nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_no = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # Status of the withdrawal request. 'pending' or 'completed'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('withdrawals', lazy='dynamic'))

    def __repr__(self):
        return f'<ID: {self.id}, amount: {self.amount}, account_no: {self.account_no}, Status: {self.status}>'
    
    @classmethod
    def create_withdrawal(cls, reference, amount, bank_name, account_no, status, trendit3_user):
        withdrawal = cls(reference=reference, amount=amount, bank_name=bank_name, account_no=account_no, status=status, trendit3_user=trendit3_user)
        
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
            'reference': self.reference,
            'amount': self.amount,
            'bank_name': self.bank_name,
            'account_no': self.account_no,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            **user_info,
        }


class Wallet(db.Model):
    __tablename__ = "wallet"

    id = db.Column(db.Integer(), primary_key=True)
    _balance = db.Column(db.Numeric(10, 2), default=00.00, nullable=True)
    currency_name = db.Column(db.String(), default='Naira', nullable=True)
    currency_code = db.Column(db.String(), default='NGN', nullable=True)
    currency_symbol = db.Column(db.String(), default=str('₦'), nullable=True)
    
    # Relationship with the user model
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', back_populates="wallet")
    
    
    @property
    def balance(self):
        return float(self._wallet_balance)

    @balance.setter
    def balance(self, value):
        self._balance = round(value, 2)
    
    def __repr__(self):
        return f'<ID: {self.id}, Balance: {self.balance}, Currency Name: {self.currency_name}, Symbol: {self.currency_symbol}>'
    
    @classmethod
    def create_wallet(cls, trendit3_user, balance=00.00, currency_name='Naira', currency_code='NGN', **kwargs):
        wallet = cls(trendit3_user=trendit3_user, balance=balance, currency_name=currency_name, currency_code=currency_code)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(wallet, key, value)
        
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
            'currency_symbol': self.currency_symbol,
            **user_info,
        }
