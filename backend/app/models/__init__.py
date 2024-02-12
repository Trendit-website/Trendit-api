'''
This package contains the database models for the Flask application.

It includes models for User, Product, Category, Transaction, Role, etc. Each model corresponds to a table in the database.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''
from app.models.media import Media
from app.models.membership import Membership
from app.models.item import Item, LikeLog, Share, Comment
from app.models.payment import Payment, Transaction, Wallet
from app.models.user import Trendit3User, Address, Profile, ReferralHistory
from app.models.task import Task, AdvertTask, EngagementTask, TaskPerformance