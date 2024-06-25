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
from ..models import Media
from config import Config


class PricingCategory(Enum):
    ADVERT = 'advert'
    ENGAGEMENT = 'engagement'


class Pricing(db.Model):
    """Data model for Pricing."""
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(20), nullable=False) # advert or engagement
    price_earn = db.Column(db.Float, nullable=False) # price for the earners
    price_pay = db.Column(db.Float, nullable=False) # price for the advertisers
    image_id = db.Column(db.Integer(), db.ForeignKey('media.id'), nullable=True)
    price_icon = db.relationship('Media', backref='price_icon')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # db.session.commit()

    def __repr__(self):
        return f'<Pricing: {self.item_name} - ${self.price}>'

    @property
    def icon(self):
        if self.image_id:
            theImage = Media.query.get(self.image_id)
            if theImage:
                return theImage.get_path()
            else:
                return ''
        else:
            return ''
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'description': self.description,
            'category': self.category,
            'price_earn': self.price_earn,
            'price_pay': self.price_pay,
            'icon': self.icon
        }