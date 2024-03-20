'''
This module contains the Error Handlers for Werkzeug exceptions
that return appropriate JSON responses on the Trendit³ Flask application.

It returns informative messages and status codes.

It includes error handling for the following:
    * BadRequestKeyError(400)
    * not found(404)
    * method not allowed(405)
    * unsupported media type(415)
    * unprocessable (422)
    * internal server error (500)


@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from . import bp
from ..utils.helpers import log_exception
from ..utils.helpers.response_helpers import error_response
from werkzeug.exceptions import ( BadRequestKeyError, SecurityError, UnprocessableEntity )


@bp.app_errorhandler(BadRequestKeyError)
def bad_request_key_error(error):
    code = error.code
    message = error.description
    log_exception(message, error)
    return error_response(f"{str(message)}", code)

@bp.app_errorhandler(SecurityError)
def security_error(error):
    code = error.code
    message = error.description
    log_exception(message, error)
    return error_response(f"{str(message)}", code)

@bp.app_errorhandler(UnprocessableEntity)
def unprocessable_entity(error):
    code = error.code
    message = error.description
    log_exception(message, error)
    return error_response(f"{str(message)}", code)
