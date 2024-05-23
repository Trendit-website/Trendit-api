'''
This module defines the Pricing model for the database.

It includes fields for the item name and price.

@author Chris
@link: https://github.com/al-chris
@package Trendit³
'''

from sqlalchemy.orm import backref
from datetime import datetime, timezone
from enum import Enum

from ..extensions import db
from config import Config


class PricingCategory(Enum):
    ADVERT = 'advert'
    ENGAGEMENT = 'engagement'


class Pricing(db.Model):
    """Data model for Pricing."""
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(250), nullable=False)
    category = db.Column(db.Enum(PricingCategory), nullable=False)
    price_earn = db.Column(db.Float, nullable=False) # price for the earners
    price_pay = db.Column(db.Float, nullable=False) # price for the advertisers
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Pricing: {self.item_name} - ${self.price}>'