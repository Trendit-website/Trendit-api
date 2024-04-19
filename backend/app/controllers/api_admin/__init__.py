'''
This package contains the controllers for the admin API of the Trendit³ Flask application.

It includes controller handlers for admin authentication, stats, user management, and settings.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from app.controllers.api_admin.task_performance import AdminTaskPerformanceController
from app.controllers.api_admin.auth import AdminAuthController
from app.controllers.api_admin.dashboard import AdminDashboardController
from app.controllers.api_admin.tasks import AdminTaskController
from app.controllers.api_admin.users import AdminUsersController
from app.controllers.api_admin.transactions import TransactionController
from app.controllers.api_admin.earn_appeal import EarnAppealController