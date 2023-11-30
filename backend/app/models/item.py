from sqlalchemy.orm import backref
from datetime import datetime

from app.extensions import db
from app.models import Media



class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    item_type  = db.Column(db.String(), nullable=True) # either product or service to be uploaded to market place
    name = db.Column(db.String(100), nullable=False)
    description  = db.Column(db.String(), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    brand_name = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(), nullable=True)
    material = db.Column(db.String(300), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    views_count = db.Column(db.Integer, default=0)
    slug = db.Column(db.String(), nullable=False, unique=True)
    item_img = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    seller_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    seller = db.relationship('Trendit3User', backref=db.backref('items', lazy='dynamic'))
    media = db.relationship('Media')
    

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
    
    def get_item_img(self):
        if self.item_img:
            theImage = Media.query.get(self.item_img)
            if theImage:
                return theImage.get_path()
            else:
                return None
        else:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_img': self.get_item_img(),
            'price': self.price,
            'category': self.category,
            'brand_name': self.brand_name,
            'sizes': self.size,
            'colors': self.color,
            'material': self.material,
            'phone': self.phone,
            'slug': self.slug,
            'views_count': self.views_count,
            'total_likes': len(list(self.likes)),
            'total_comments': len(list(self.comments)),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'seller_id': self.seller_id,
        }

class LikeLog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)

    # relationships
    liked_item = db.relationship('Item', backref=db.backref('likes', lazy='dynamic'))
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('likes', lazy='dynamic'))
    
    def __repr__(self):
        return f'<LikeLog ID: {self.id}, Item_ID: {self.item_id}, User_ID: {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.item_id,
            'description': self.user_id,
        }

class Share(db.Model):
    __tablename__ = 'share'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)

    # relationships
    shared_item = db.relationship('Item', backref=db.backref('shares', lazy='dynamic'))
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('shares', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Share ID: {self.id}, Item_ID: {self.item_id}, User_ID: {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.item_id,
            'description': self.user_id,
        }

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    commented_item = db.relationship('Item', backref=db.backref('comments', lazy='dynamic'))
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('comments', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Comment ID: {self.id}, Item_ID: {self.item_id}, User_ID: {self.user_id}, Created_at: {self.created_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.item_id,
            'description': self.user_id,
        }
