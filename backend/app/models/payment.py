'''
from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # 'activation_fee' or 'monthly_fee'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('Trendit3User')
'''