import uuid
from flask import request
from sqlalchemy.orm import backref
from datetime import datetime

from app.extensions import db
## from app.models.image import Image



class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=str(uuid.uuid4()))
    item_type  = db.Column(db.String(), nullable=True) # either product or service to be uploaded to market place
    name = db.Column(db.String(100), nullable=False)
    description  = db.Column(db.String(), nullable=True)
    item_img = db.Column(db.String(), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    brand_name = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(), nullable=True)
    material = db.Column(db.String(300), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    slug = db.Column(db.String(), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    seller_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    seller = db.relationship('Trendit3User', backref=db.backref('items', lazy='dynamic'))
    

    def __repr__(self):
        return f'<Item ID: {self.id}, name: {self.name}, type: {self.item_type}, time: {self.timestamp}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    '''
    def getThumbImage(self):
        theImage = Image.query.get(self.item_img)
        if theImage:
            return theImage.get_path("thumb")
        else:
            return None
    
    def getMediumImage(self):
        theImage = Image.query.get(self.item_img)
        if theImage:
            return theImage.get_path("medium")
        else:
            return None

    def getLargeImage(self):
        theImage = Image.query.get(self.item_img)
        if theImage:
            return theImage.get_path("large")
        else:
            return None
    '''
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            # 'item_img': self.getMediumImage(),
            'price': self.price,
            'category': self.category,
            'brand_name': self.brand_name,
            'sizes': self.size,
            'colors': self.color,
            'material': self.material,
            'phone': self.phone,
            'slug': self.slug,
        }
