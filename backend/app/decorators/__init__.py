"""
This package contains the decorators for the Trendit³ Flask application.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
"""
from .auth import roles_required
from .membership import membership_required