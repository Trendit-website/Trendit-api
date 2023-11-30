from flask import Flask, jsonify
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError, CSRFError
from jwt import ExpiredSignatureError

from app.routes.error_handlers import bp
from app.controllers.error_handlers.handlers import ErrorHandlers

@bp.app_errorhandler(400)
def bad_request(error):
    return ErrorHandlers.bad_request(error)

@bp.app_errorhandler(404)
def not_found(error):
    return ErrorHandlers.not_found(error)

@bp.app_errorhandler(405)
def method_not_allowed(error):
    return ErrorHandlers.method_not_allowed(error)

@bp.app_errorhandler(422)
def unprocessable(error):
    return ErrorHandlers.unprocessable(error)

@bp.app_errorhandler(500)
def internal_server_error(error):
    return ErrorHandlers.internal_server_error(error)


@bp.app_errorhandler(NoAuthorizationError)
def jwt_auth_error(error):
    return ErrorHandlers.jwt_auth_error(error)

@bp.app_errorhandler(ExpiredSignatureError)
def expired_jwt(error):
    return ErrorHandlers.expired_jwt(error)

@bp.app_errorhandler(InvalidHeaderError)
def jwt_invalid_header(error):
    return ErrorHandlers.jwt_invalid_header(error)

@bp.app_errorhandler(WrongTokenError)
def wrong_jwt_token(error):
    return ErrorHandlers.wrong_jwt_token(error)

@bp.app_errorhandler(CSRFError)
def jwt_csrf_error(error):
    return ErrorHandlers.jwt_csrf_error(error)
