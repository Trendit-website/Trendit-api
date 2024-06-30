from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.orm import backref
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..utils.helpers.basic_helpers import generate_random_string, console_log, log_exception
from ..utils.payments.rates import convert_amount

task_goals = ["follow", "like", "comment", "share", "subscribe", "review", "download", "retweet" "join_group_channel", "like_follow", "download_review"]

class TaskOption(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(36), unique=True, nullable=False, default=f"{generate_random_string(12)}-{generate_random_string(5)}")
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
            {"advertiser_name": "Get People to post your advert on 𝕏", "earner_name": "Post adverts on your 𝕏 account", "advertiser_description": "Get genuine people with over 500 followers on their 𝕏 account to post your adverts to their audience. Expand your reach today through Trendit³", "earner_description": "Promote advertisements for different businesses and top brands on your X page and earn ₦110 for each post. The more you share, the more you earn. Ensure that your 𝕏 account has at least 500 active followers to qualify for this task.", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},
            
            {"advertiser_name": "Get People to post your advert on Instagram", "earner_name": "Post adverts on your Instagram account", "advertiser_description": "Get real people with at least 500 active followers on their Instagram accounts to post your advert. This ensures your advert gets massive views quickly. You can specify how many people you want to share your advert.", "earner_description": "Promote advertisements for different businesses and top brands on your Instagram page and earn ₦110 for each post. The more you share, the more you earn. Ensure that your Instagram account has at least 500 active followers to qualify for this task.", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get people to post your Advert on Facebook", "earner_name": "Post adverts on your Facebook page", "advertiser_description": "Get genuine people with over 500 followers or friends on their Facebook accounts to post your adverts. Expand your audience reach today through Trendit³.", "earner_description": "Promote advertisements for different businesses and top brands on your Facebook page and earn ₦110 for each post. The more you share, the more you earn. Ensure that your Facebook account has at least 500 active followers to qualify for this task.", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get People to post your advert on TikTok", "earner_name": "Post adverts on your TikTok page", "advertiser_description": "Get real users with at least 500 active followers on their TikTok accounts to share your adverts. This boosts your advert's visibility quickly. Specify how many people you want to share your advert.", "earner_description": "Promote advertisements for different businesses and top brands on your TikTok page and earn ₦110 for each post. The more you share, the more you earn. Ensure that your TikTok account has at least 500 active followers to qualify for this task.", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get People to post your advert on WhatsApp", "earner_name": "Post adverts on your WhatsApp status", "advertiser_description": "Get real people to post your ads on their WhatsApp Status, ensuring your advert gets significant visibility quickly. You can specify how many people you want to share your advert.", "earner_description": "Post adverts of various businesses and top brands on your WhatsApp status and earn ₦60 per advert past. The more you post, the more you earn.", "advertiser_price": 80, "earner_price": 60, "task_type": "advert"},

            {"advertiser_name": "Get People to post your advert on Threads", "earner_name": "Post adverts on your Threads account", "advertiser_description": "Get genuine users with over 500 followers on their Threads account to share your advert with their audience. Boost your visibility and expand your reach today through Trendit³.", "earner_description": "Promote advertisements for different businesses and top brands on your Threads page and earn ₦110 for each post. The more you share, the more you earn. Ensure that your Threads account has at least 500 active followers to qualify for this task.", "advertiser_price": 140, "earner_price": 110, "task_type": "advert"},

            {"advertiser_name": "Get Genuine People to Follow Your Social Media Accounts", "earner_name": "Follow social media accounts", "advertiser_description": "Get real people to follow your social media pages. you can get any numbers of people to follow your social media pages with no need for your login Details, on any social platform like Facebook, Tiktok, Instagram and many more.", "earner_description": "Follow people and pages on selected social media accounts like Facebook, Instagram, TikTok, and others to earn ₦3.5 per follow. Unlock your earning potential by performing one task at a time", "advertiser_price": 5, "earner_price": 3.5, "task_type": "engagement"},

            {"advertiser_name": "Get Genuine People to Like Your Social Media Posts", "earner_name": "Like social media posts", "advertiser_description": "Get Genuine people to like your social media post. You can get as many likes as you desire simply by entering the link to your post either on Instagram, Facebook, Twitter or any platform.", "earner_description": "Like posts on social media platforms like Instagram, Facebook, TikTok, and others to earn ₦3.5 per like. Turn your daily routine into rewards!", "advertiser_price": 5, "earner_price": 3.5, "task_type": "engagement"},

            {"advertiser_name": "Get Real People to Like and Follow Your Facebook Business Page", "earner_name": "Like and follow Facebook business page", "advertiser_description": "Get real people to like and follow your Facebook business page. you can get any number of people to like and follow your Facebook business page without disclosing your Login details", "earner_description": "Like and follow Facebook pages for businesses and organizations to earn ₦3.5 per like and follow. Unlock your earning potential by performing one task at a time.", "advertiser_price": 40, "earner_price": 3.5, "task_type": "engagement"},
            
            {"advertiser_name": "Get Genuine People to Comment on Your Social Media Posts", "earner_name": "Post Comments on Pages and Post on Several Social Media Platforms", "advertiser_description": "Get Genuine people to comment your social media post. You can get as many comments as you desire simply by entering the link to your post either on Instagram, Facebook, TikTok,X or any other platform.", "earner_description": "Post comments on personal, business, or organization pages and posts on social media platforms like X, Instagram, Facebook, TikTok, and others to earn ₦20 per comment. Hustle more, earn more.", "advertiser_price": 40, "earner_price": 20, "task_type": "engagement"},
        ]

        try:
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
                        task_type=option["task_type"],
                        key=f"{generate_random_string(20)}-{generate_random_string(5)}"
                    )
                    db.session.add(task_option)
                    db.session.commit()
        except Exception as e:
            log_exception("Some error populating task options", e)
            db.session.rollback()



