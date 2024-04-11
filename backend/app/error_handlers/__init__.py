'''
This module contains the Error Handlers that return 
proper Error responses on the Trendit³ Flask application.

It includes error handling for:
    * HTTP Status Errors
    * JWT Errors

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from flask import Blueprint

bp = Blueprint('errorHandlers', __name__)

from ..error_handlers import http_errors, jwt_errors, rate_limit, slug_errors, social_tasks_errors, werkzeug_errors, sqlalchemy_errors