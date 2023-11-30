from flask import request
from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    media_path = db.Column(db.String(256), nullable=True) # False
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Media {self.id}, Filename: {self.filename}>"
    
    def get_path(self):
        return self.media_path

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'media_path': self.media_path,
            'created_at': self.created_at,
        }
