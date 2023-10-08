from flask import Flask, jsonify
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
