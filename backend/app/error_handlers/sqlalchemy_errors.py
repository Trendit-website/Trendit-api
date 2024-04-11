'''
This module contains the sqlalchemy Error Handlers that return 
proper Error responses on the Trendit³ Flask application.

It includes error handling for the following sqlalchemy errors:
    * OperationalError
    * ArgumentError
    * TimeoutError
    * ProgrammingError

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from . import bp
from ..utils.helpers import log_exception
from ..utils.helpers.response_helpers import error_response

from sqlalchemy.exc import OperationalError, IntegrityError, InvalidRequestError, ArgumentError, TimeoutError, ProgrammingError


@bp.app_errorhandler(OperationalError)
def sqlalchemy_operational_error(error):
    log_exception('OperationalError', error)
    return error_response(f"{str(error)}", 500)

@bp.app_errorhandler(ArgumentError)
def sqlalchemy_argument_error(error):
    log_exception('ArgumentError', error)
    return error_response(f"{str(error)}", 500)

@bp.app_errorhandler(ProgrammingError)
def sqlalchemy_programming_error(error):
    log_exception('ProgrammingError', error)
    return error_response(f"{str(error)}", 500)

@bp.app_errorhandler(TimeoutError)
def sqlalchemy_timeout_error(error):
    log_exception('TimeoutError', error)
    return error_response(f"{str(error)}", 500)

@bp.app_errorhandler(InvalidRequestError)
def sqlalchemy_invalid_request_error(error):
    log_exception('InvalidRequestError', error)
    return error_response(f"{str(error)}", 500)

@bp.app_errorhandler(IntegrityError)
def sqlalchemy_integrity_error(error):
    log_exception('IntegrityError', error)
    return error_response(f"{str(error)}", 500)