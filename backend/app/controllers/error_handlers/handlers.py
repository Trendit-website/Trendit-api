import logging
from flask import Flask, jsonify, render_template
from app.routes.error_handlers import bp
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.response_helpers import error_response

class ErrorHandlers:
    @staticmethod
    def bad_request(error):
        return jsonify({
            "status": 'failed',
            "status_code": 400,
            "message": "Bad request."
        }), 400

    @staticmethod
    def not_found(error):
        return jsonify({
            "status": 'failed',
            "status_code": 404,
            "message": "resource not found"
        }), 404

    @staticmethod
    def method_not_allowed(error):
        return jsonify({
            "status": 'failed',
            "status_code": 405,
            "message": "method not allowed"
        }), 405

    @staticmethod
    def unsupported_media_type(error):
        return error_response(f"Unsupported Media Type: {str(error)}", 415)
    
    @staticmethod
    def unprocessable(error):
        logging.exception("An unprocessable error occurred:", str(error))
        return jsonify({
            "status": 'failed',
            "status_code": 422,
            "message": "The request was well-formed but was unable to be followed due to semantic errors."
        }), 422

    @staticmethod
    def internal_server_error(error):
        return error_response("Internal server error", 500)
    
    
    @staticmethod
    def jwt_auth_error(error):
        console_log('JWT error', error)
        return jsonify({
            "status": 'failed',
            'message': 'User is not logged in',
            'status_code': 401,
        }), 401
    
    @staticmethod
    def expired_jwt(error):
        return jsonify({
            "status": 'failed',
            'message': 'Access token has expired. Please log in again.',
            'status_code': 401,
        }), 401
    
    @staticmethod
    def jwt_invalid_header(error):
        return jsonify({
            "status": 'failed',
            'message': 'Invalid JWT header. Token may be tampered.',
            'status_code': 401,
        }), 401
    
    @staticmethod
    def wrong_jwt_token(error):
        return jsonify({
            "status": 'failed',
            'message': 'Wrong type of JWT token.',
            'status_code': 401,
        }), 401
    
    @staticmethod
    def jwt_csrf_error(error):
        return jsonify({
            "status": 'failed',
            'message': 'CSRF token is missing or invalid.',
            'status_code': 401,
        }), 401


    @staticmethod
    def json_decode_error(error):
        return error_response("response body does not contain valid json.", 500)