'''
This package contains the controllers for the admin API of the Trendit³ Flask application.

It includes controller handlers for admin authentication, stats, user management, and settings.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from .task_performance import AdminTaskPerformanceController
from .auth import AdminAuthController
from .dashboard import AdminDashboardController
from .tasks import AdminTaskController
from .users import AdminUsersController
from .transactions import TransactionController
from .earn_appeal import EarnAppealController
from .pricing import PricingController
from .social_profile import AdminSocialProfileController
from .wallet import AdminWalletController