'''
This module defines the `membership_required` decorator for the Trendit³ Flask application.

Used for handling role-based access control.
The `membership_required` decorator is used to ensure that the current user has paid the membership fee.
If the user hasn't paid, it returns a 403 error.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import Trendit3User
from app.utils.helpers.response_helpers import error_response

def membership_required():
    """
    Decorator to ensure that the current user has all of the specified roles.

    This decorator will return a 403 error if the current user has not
    paid the membership fee

    Returns:
        function: The decorated function.

    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = Trendit3User.query.get(current_user_id)
            
            if user and user.membership.membership_fee_paid:
                return fn(*args, **kwargs)
            else:
                return error_response("Access denied: Membership fee hasn't been paid", 403)
        return wrapper
    return decorator
