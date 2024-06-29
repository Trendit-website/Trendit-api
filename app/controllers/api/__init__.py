'''
This package contains the controllers for the API of the Trendit³ Flask application.

It includes controller handlers for authentication, payments, profile management, 
stats, items, tasks, location, and referral system.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from .auth import AuthController
from .payment import PaymentController
from .item import ItemController
from .item_interactions import ItemInteractionsController
from .task import TaskController
from .task_performance import TaskPerformanceController
from .profile import ProfileController
from .referral import ReferralController
from .location import LocationController
from .stats import StatsController
from .notification import NotificationController
from .settings import ManageSettingsController
from .transactions import TransactionController
from .pricing import PricingController
from .social_auth import SocialAuthController
from .social_profile import SocialProfileController
from .social_platforms import SocialMediaPlatformsController
from .task_option import TaskOptionsController