'''
from flask import request
from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    original_webp = db.Column(db.String(256), nullable=True) # False
    original_jpg = db.Column(db.String(256), nullable=True) # False
    thumb_webp = db.Column(db.String(256), nullable=True) # False
    thumb_jpg = db.Column(db.String(256), nullable=True) # False
    medium_webp = db.Column(db.String(256), nullable=True) # False
    medium_jpg = db.Column(db.String(256), nullable=True) # False
    large_webp = db.Column(db.String(256), nullable=True) # False
    large_jpg = db.Column(db.String(256), nullable=True) # False
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Image {self.id}, Filename: {self.filename}>"
    
    def get_path(self, size):
        # Check if the client supports WebP
        if 'image/webp' in request.accept_mimetypes:
            if size == "thumb":
                return self.thumb_webp
            elif size == "medium":
                return self.medium_webp
            elif size == "large":
                return self.large_webp
            else:
                raise ValueError("Invalid image size")
        else:
            # Serve the JPEG version of the image
            if size == "thumb":
                return self.thumb_jpg
            elif size == "medium":
                return self.medium_jpg
            elif size == "large":
                return self.large_jpg
            else:
                raise ValueError("Invalid image size")

'''