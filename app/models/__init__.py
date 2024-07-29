'''
This package contains the database models for the Flask application.

It includes models for User, Product, Category, Transaction, Role, etc. Each model corresponds to a table in the database.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''
from ..models.media import Media
from ..models.membership import Membership
from ..models.item import Item, LikeLog, Share, Comment
from ..models.payment import Payment, Transaction, Wallet, Withdrawal, TransactionType
from ..models.user import Trendit3User, Address, Profile, ReferralHistory, TempUser, OneTimeToken, BankAccount, Recipient
from ..models.task import Task, AdvertTask, EngagementTask, TaskStatus, TaskPaymentStatus, TaskPerformance
from .task_option import TaskOption
from ..models.notification import UserMessageStatus, Notification, user_notification, SocialVerificationStatus, SocialVerification, NotificationType
from ..models.settings import UserSettings, NotificationPreference, SecuritySetting, UserPreference
from ..models.role import Role, RoleNames, user_roles, create_roles
from ..models.pricing import Pricing, PricingCategory
from .social import SocialMediaProfile, SocialIDs, SocialLinks, SocialLinkStatus