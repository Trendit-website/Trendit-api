'''
This module defines the Pricing model for the database.

It includes fields for the item name and price.

@author Chris
@link: https://github.com/al-chris
@package Trendit³
'''

from sqlalchemy.orm import backref
from datetime import datetime, timezone

from ..extensions import db
from config import Config


class Pricing(db.Model):
    """Data model for Pricing."""
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Pricing: {self.item_name} - ${self.price}>'