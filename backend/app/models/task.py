from app.extensions import db
from sqlalchemy.orm import backref
from datetime import datetime

from app.models.image import Image

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(80), nullable=False)
    fee = db.Column(db.Float, nullable=False)
    media_id = db.Column(db.String(255), nullable=True)
    task_ref = db.Column(db.String(120), unique=True, nullable=False)
    payment_status = db.Column(db.String(80), nullable=False)
    
    @classmethod
    def create_task(cls, user_id, type, platform, fee, task_ref, payment_status, media_path=None, **kwargs):
        task = cls(user_id=user_id, type=type, platform=platform, fee=fee, task_ref=task_ref, payment_status=payment_status, media_path=media_path, **kwargs)
        
        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(task, key, value)
        
        db.session.add(task)
        db.session.commit()
        return task
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_task_media(self):
        if self.media_id:
            theImage = Image.query.get(self.media_id)
            if theImage:
                return theImage.get_path("original")
            else:
                return None
        else:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'platform': self.platform,
            'media_path': self.media_id,
            'task_reference': self.task_ref,
            'payment_status': self.payment_status
        }

class AdvertTask(Task):
    id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    posts_count = db.Column(db.Integer, nullable=False)
    target_country = db.Column(db.String(120), nullable=False)
    target_state = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(120), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<ID: {self.id}, User ID: {self.user_id}, Platform: {self.platform}, Posts Count: {self.posts_count}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'platform': self.platform,
            'media_path': self.media_path,
            'posts_count': self.posts_count,
            'target_country': self.target_country,
            'target_state': self.target_state,
            'gender': self.gender,
            'caption': self.caption,
            'hashtags': self.hashtags,
            'task_reference': self.task_ref,
            'payment_status': self.payment_status
        }


class EngagementTask(Task):
    id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    goal = db.Column(db.String(80), nullable=False)
    account_link = db.Column(db.String(120), nullable=False)
    engagements_count = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<ID: {self.id}, User ID: {self.user_id}, Goal: {self.goal}, Platform: {self.platform}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'platform': self.platform,
            'media_path': self.media_path,
            'goal': self.goal,
            'account_link': self.account_link,
            'engagements_count': self.engagements_count,
            'task_reference': self.task_ref,
            'payment_status': self.payment_status
        }


class TaskPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    task_id = db.Column(db.Integer, nullable=False)  # either an AdvertTask id or an EngagementTask id
    task_type = db.Column(db.String(80), nullable=False)  # either 'advert' or 'engagement'
    proof_screenshot_path = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(80), default='pending')
    
    def __repr__(self):
        return f'<ID: {self.id}, User ID: {self.user_id}, Task ID: {self.task_id}, Task Type: {self.task_type}, status: {self.status}>'
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'task_type': self.task_type,
            'proof_screenshot_path': self.proof_screenshot_path,
            'status': self.status,
        }
