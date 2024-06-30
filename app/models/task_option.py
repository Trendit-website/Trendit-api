from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.orm import backref
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..utils.helpers.basic_helpers import generate_random_string
from ..utils.payments.rates import convert_amount

task_goals = ["follow", "like", "comment", "share", "subscribe", "review", "download", "retweet" "join_group_channel", "like_follow", "download_review"]

class TaskOption(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(36), unique=True, nullable=False, default=f"{generate_random_string()}-{generate_random_string(5)}")
    advertiser_name = db.Column(db.String(150), nullable=False)
    earner_name = db.Column(db.String(150), nullable=False)
    advertiser_description = db.Column(db.String(255), nullable=False)
    earner_description = db.Column(db.String(255), nullable=False)
    advertiser_price = db.Column(db.Numeric(10, 2), nullable=False)
    earner_price = db.Column(db.Numeric(10, 2), nullable=False)
    task_type = db.Column(db.String(20), nullable=False)  # 'advert' or 'engagement'
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self, user_type, currency_code):
        name = self.advertiser_name if user_type == "advertiser" else self.earner_name
        description = self.advertiser_description if user_type == "advertiser" else self.earner_description
        price = self.advertiser_price if user_type == "advertiser" else self.earner_price
        
        amount = convert_amount(price, currency_code),
        
        return {
            "name": name,
            "description": description,
            "price": amount,
            "task_type": self.task_type,
            "key": self.key
        }



def populate_task_options(clear: bool = False) -> None:
    if inspect(db.engine).has_table('task_option'):
        if clear:
            # Clear existing task option before creating new ones
            TaskOption.query.delete()
            db.session.commit()
        
        task_options = [
            {"advertiser_name": "Get People to post your advert on 𝕏", "earner_name": "Post adverts on your 𝕏 account", "advertiser_description": "", "earner_description": "", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},
            
            {"advertiser_name": "Get People to post your advert on Instagram", "earner_name": "Post adverts on your Instagram account", "advertiser_description": "", "earner_description": "", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get people to post your Advert on Facebook", "earner_name": "Post adverts on your Facebook page", "advertiser_description": "", "earner_description": "", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get People to post your advert on TikTok", "earner_name": "Post adverts on your TikTok page", "advertiser_description": "", "earner_description": "", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get People to post your advert on WhatsApp", "earner_name": "Post adverts on your WhatsApp status", "advertiser_description": "", "earner_description": "", "advertiser_price": 80, "earner_price": 60, "task_type": "advert"},

            {"advertiser_name": "Get People to post your advert on Threads", "earner_name": "Post adverts on your Threads account", "advertiser_description": "", "earner_description": "", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get Genuine People to Follow Your Social Media Accounts", "earner_name": "Follow social media accounts", "advertiser_description": "", "earner_description": "", "advertiser_price": 5, "earner_price": 3.5, "task_type": "engagement"},

            {"advertiser_name": "Get Genuine People to Like Your Social Media Posts", "earner_name": "Like social media posts", "advertiser_description": "", "earner_description": "", "advertiser_price": 5, "earner_price": 3.5, "task_type": "engagement"},

            {"advertiser_name": "Get Real People to Like and Follow Your Facebook Business Page", "earner_name": "Like and follow Facebook business page", "advertiser_description": "", "earner_description": "", "advertiser_price": 40, "earner_price": 3.5, "task_type": "engagement"},
            
            {"advertiser_name": "Get Genuine People to Comment on Your Social Media Posts", "earner_name": "Post Comments on Pages and Post on Several Social Media Platforms", "advertiser_description": "", "earner_description": "", "advertiser_price": 40, "earner_price": 20, "task_type": "engagement"},
        ]

        db_task_option = TaskOption.query.all()
        if not db_task_option:
            for option in task_options:
                task_option = TaskOption(
                    advertiser_name=option["advertiser_name"],
                    earner_name=option["earner_name"],
                    advertiser_description=option["advertiser_description"],
                    earner_description=option["earner_description"],
                    advertiser_price=option["advertiser_price"],
                    earner_price=option["earner_price"],
                    task_type=option["task_type"]
                )
                db.session.add(task_option)
                db.session.commit()



