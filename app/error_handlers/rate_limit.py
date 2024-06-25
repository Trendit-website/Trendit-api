'''
This module contains error handlers for rate limit exceeded scenarios in the Trendit³ Flask application.

Author: Emmanuel Olowu
GitHub: https://github.com/zeddyemy
Package: Trendit³

The error handler in this module provides custom responses for RateLimitExceeded exceptions,
returning a 429 Too Many Requests status code.

'''

from flask_limiter.errors import RateLimitExceeded

from ..error_handlers import bp
from ..utils.helpers.basic_helpers import console_log, log_exception
from ..utils.helpers.response_helpers import error_response


# Define custom error handler for RateLimitExceeded exception
@bp.app_errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(error):
    log_exception('Rate Limit Exceeded', error)
    return error_response(f'Rate Limit Exceeded: {str(error)}', 429) # Return 429 Too Many Requests status code
