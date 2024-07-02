from datetime import datetime
from enum import Enum
from sqlalchemy.orm import backref
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Media
from ..utils.helpers.basic_helpers import generate_random_string


class TaskStatus(Enum):
    """ENUMS for the Status filed in Task Model"""
    APPROVED = 'approved'
    PENDING = 'pending'
    DECLINED = 'declined'

class TaskPaymentStatus(Enum):
    """ENUMS for the payment_status filed in Task Model"""
    COMPLETE = 'complete'
    PENDING = 'pending'
    FAILED = 'failed'
    ABANDONED = 'abandoned'

class TaskPerformanceStatus(Enum):
    """ENUMS for the payment_status filed in Task Model"""
    PENDING = 'pending'
    IN_REVIEW = 'in_review'
    FAILED = 'failed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    TIMED_OUT = 'timed_out'

# association table for the many-to-many relationship
task_medias = db.Table(
    'task_medias',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('media_id', db.Integer, db.ForeignKey('media.id'))
)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False) # advert task, or engagement task
    platform = db.Column(db.String(80), nullable=False)
    fee = db.Column(db.Numeric(10, 2), nullable=False)
    fee_paid = db.Column(db.Numeric(10, 2), nullable=True)
    task_key = db.Column(db.String(120), unique=True, nullable=False)
    target_country = db.Column(db.String(120), nullable=True, default="Nigeria")
    target_state = db.Column(db.String(120), nullable=True, default="Lagos")
    religion = db.Column(db.String(120), nullable=True, default="")
    gender = db.Column(db.String(120), nullable=True, default="")
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_allocated = db.Column(db.Integer, default=0, nullable=True)
    total_success = db.Column(db.Integer, default=0, nullable=True)
    
    authorization_url = db.Column(db.String(250), nullable=True, default="") # if payment for task is done with payment gateway
    payment_status = db.Column(db.Enum(TaskPaymentStatus), nullable=False)  # complete, pending, failed, abandoned
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)  # approved, pending, declined
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('tasks', lazy='dynamic'))
    
    media = db.relationship('Media', backref='task', lazy=True, cascade="all, delete-orphan", single_parent=True)
    
    __mapper_args__ = {
        'polymorphic_on': task_type,
        'polymorphic_identity': 'task'
    }
    
    @property
    def total_performances(self) -> int:
        """Returns the total number times the task has been performed."""
        return self.performances.count()
    
    @classmethod
    def create_task(cls, trendit3_user_id, task_type, platform, fee, fee_paid, payment_status, **kwargs):
        the_task_ref = generate_random_string(20)
        counter = 1
        max_attempts = 6  # maximum number of attempts to create a unique task_key
        
        while cls.query.filter_by(task_key=the_task_ref).first() is not None:
            if counter > max_attempts:
                raise ValueError(f"Unable to create a unique task after {max_attempts} attempts.")
            the_task_ref = f"{generate_random_string(20)}-{generate_random_string(4)}-{counter}"
            counter += 1
        
        task = cls(trendit3_user_id=trendit3_user_id, task_type=task_type, platform=platform, fee=fee, fee_paid=fee_paid, task_key=the_task_ref, payment_status=payment_status, **kwargs)
        
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

    def get_task_media(self) -> list[str]:
        media_paths = []
        for media in self.media:
            media_paths.append(media.get_path())
        return media_paths if media_paths else None
    
    def to_dict(self):
        advert_task_dict = {}
        advert_task = AdvertTask.query.get(self.id)
        if advert_task:
            advert_task_dict.update({
                'posts_count': advert_task.posts_count,
                'caption': advert_task.caption,
                'hashtags': advert_task.hashtags,
            })
        
        engagement_task_dict = {}
        engagement_task = EngagementTask.query.get(self.id)
        if engagement_task:
            engagement_task_dict.update({
                'goal': engagement_task.goal,
                'account_link': engagement_task.account_link,
                'engagements_count': engagement_task.engagements_count,
            })
            
        return {
            'id': self.id,
            'task_type': self.task_type,
            'platform': self.platform,
            'fee': self.fee,
            'fee_paid': self.fee_paid,
            'media_path': self.get_task_media(),
            'task_key': self.task_key,
            'target_country': self.target_country,
            'target_state': self.target_state,
            'gender': self.gender,
            'religion': self.religion,
            'authorization_url': self.authorization_url,
            'payment_status': str(self.payment_status.value),
            'status': str(self.status.value),
            'total_allocated': self.total_allocated,
            'total_success': self.total_success,
            'date_created': self.date_created,
            'updated_at': self.updated_at,
            'creator': {
                'id': self.trendit3_user_id,
                'username': self.trendit3_user.username,
                'email': self.trendit3_user.email
            },
            **advert_task_dict,
            **engagement_task_dict 
        }


class AdvertTask(Task):
    __tablename__ = 'advert_task'
    
    id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    posts_count = db.Column(db.Integer, nullable=False)
    caption = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.Text, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'advert'
    }
    
    def __repr__(self):
        return f'<ID: {self.id}, User ID: {self.trendit3_user_id}, Platform: {self.platform}, Posts Count: {self.posts_count}>'
    
    def basic_to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'platform': self.platform,
            'task_key': self.task_key,
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'platform': self.platform,
            'fee': self.fee,
            'fee_paid': self.fee_paid,
            'media_path': self.get_task_media(),
            'task_key': self.task_key,
            'authorization_url': self.authorization_url,
            'payment_status': str(self.payment_status.value),
            'status': str(self.status.value),
            'total_allocated': self.total_allocated,
            'total_success': self.total_success,
            'posts_count': self.posts_count,
            'target_country': self.target_country,
            'target_state': self.target_state,
            'gender': self.gender,
            'religion': self.religion,
            'caption': self.caption,
            'hashtags': self.hashtags,
            'date_created': self.date_created,
            'updated_at': self.updated_at,
            'creator': {
                'id': self.trendit3_user_id,
                'username': self.trendit3_user.username,
                'email': self.trendit3_user.email
            }
        }


class EngagementTask(Task):
    __tablename__ = 'engagement_task'
    
    id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    goal = db.Column(db.String(80), nullable=False)
    account_link = db.Column(db.String(120), nullable=False)
    engagements_count = db.Column(db.Integer, nullable=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'engagement'
    }
    
    def __repr__(self):
        return f'<ID: {self.id}, User ID: {self.trendit3_user_id}, Goal: {self.goal}, Platform: {self.platform}>'
    
    def basic_to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'goal': self.goal,
            'task_key': self.task_key,
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'platform': self.platform,
            'fee': self.fee,
            'fee_paid': self.fee_paid,
            'media_path': self.get_task_media(),
            'task_key': self.task_key,
            'authorization_url': self.authorization_url,
            'payment_status': str(self.payment_status.value),
            'status': str(self.status.value),
            'total_allocated': self.total_allocated,
            'total_success': self.total_success,
            'goal': self.goal,
            'account_link': self.account_link,
            'engagements_count': self.engagements_count,
            'target_country': self.target_country,
            'target_state': self.target_state,
            'gender': self.gender,
            'religion': self.religion,
            'date_created': self.date_created,
            'updated_at': self.updated_at,
            'creator': {
                'id': self.trendit3_user_id,
                'username': self.trendit3_user.username,
                'email': self.trendit3_user.email
            }
        }


class TaskPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False, default=generate_random_string(20))
    task_type = db.Column(db.String(80), nullable=False)  # either 'advert' or 'engagement'
    reward_money = db.Column(db.Float(), default=00.00, nullable=True)
    account_name = db.Column(db.String(80), nullable=True)
    post_link = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(80), default='pending') # pending, in_review, timed_out, cancelled, rejected or completed
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_completed = db.Column(db.DateTime, nullable=True)
    
    proof_screenshot_id = db.Column(db.Integer(), db.ForeignKey('media.id'), nullable=True)
    proof_screenshot = db.relationship('Media', backref='proof_screenshot')
    
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)  # either an AdvertTask id or an EngagementTask id
    task = db.relationship('Task', backref=db.backref('performances', lazy='dynamic'))
    
    user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id'), nullable=False)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('performed_tasks', lazy='dynamic'))
    
    
    def __repr__(self):
        return f'<ID: {self.id}, User ID: {self.user_id}, Task ID: {self.task_id}, Task Type: {self.task_type}, Status: {self.status}>'
    
    @classmethod
    def create_task_performance(cls, user_id, task_id, task_type, reward_money, proof_screenshot, account_name, post_link, status):
        the_task_key = f"{generate_random_string(20)}_pt"
        counter = 1
        max_attempts = 6  # maximum number of attempts to create a unique task_key
        
        while cls.query.filter_by(key=the_task_key).first() is not None:
            if counter > max_attempts:
                raise ValueError(f"Unable to create a unique task after {max_attempts} attempts.")
            the_task_key = f"{generate_random_string(20)}-{generate_random_string(4)}-{counter}"
            counter += 1
        
        task = cls(user_id=user_id, task_id=task_id, key=the_task_key, task_type=task_type, reward_money=reward_money, proof_screenshot=proof_screenshot, account_name=account_name, post_link=post_link, status=status)
        
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

    
    def get_proof_screenshot(self):
        if self.proof_screenshot_id:
            theImage = Media.query.get(self.proof_screenshot_id)
            if theImage:
                return theImage.get_path()
            else:
                return None
        else:
            return None
    
    def get_task(self):
        task_model = (AdvertTask if self.task_type == 'advert' else EngagementTask if self.task_type == 'engagement' else Task)
        task = task_model.query.get(self.task_id)
        task_dict = task.to_dict()
        
        return task_dict
        
    def to_dict(self, add_task=True):
        task = {'task': self.get_task(),} if add_task else {'task_key': self.task.task_key} # optionally include task info in dict
        return {
            'id': self.id,
            'key': self.key,
            'reward_money': self.reward_money,
            'proof_screenshot_path': self.get_proof_screenshot(),
            'account_name': self.account_name,
            'post_link': self.post_link,
            'status': self.status,
            'started_at': self.started_at,
            'date_completed': self.date_completed,
            'user': {
                'id': self.user_id,
                'username': self.trendit3_user.username,
                'email': self.trendit3_user.email,
                'profile_picture': self.trendit3_user.profile.profile_pic,
            },
            **task,
        }
