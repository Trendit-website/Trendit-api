from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy.exc import IntegrityError

from ..extensions import db

task_goals = ["follow", "like", "comment", "share", "subscribe", "review", "download", "retweet" "join_group_channel", "like_follow", "download_review"]

class TaskOption(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    task_type = db.Column(db.String(50), nullable=False) # advert task, or engagement task
    slug = db.Column(db.String(255), unique=True, nullable=False)


class TaskGoal(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    task_type = db.Column(db.String(50), nullable=False) # advert task, or engagement task