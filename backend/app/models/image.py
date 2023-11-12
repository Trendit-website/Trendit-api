from flask import request
from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    original_jpg = db.Column(db.String(256), nullable=True) # False
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Image {self.id}, Filename: {self.filename}>"
    
    def get_path(self, size="original"):
        # Check if the client supports WebP
        if size == "original":
            return self.original_jpg
        else:
            raise ValueError("Invalid image size")

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_jpg': self.original_jpg,
            'created_at': self.created_at,
        }
