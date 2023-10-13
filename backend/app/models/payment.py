from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # 'activation_fee' or 'monthly_fee'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Trendit3User')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.trendit3_user_id,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'timestamp': self.timestamp
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tx_ref = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.String(120), unique=False, nullable=False)
    payment_type = db.Column(db.String(120), unique=False, nullable=False)
    status = db.Column(db.String(80), unique=False, nullable=False)