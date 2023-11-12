from flask import Flask, jsonify, render_template
from app.routes.error_handlers import bp

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
    def unprocessable(error):
        return jsonify({
            "status": 'failed',
            "status_code": 422,
            "message": "The request was well-formed but was unable to be followed due to semantic errors."
        }), 422

    @staticmethod
    def internal_server_error(error):
        return jsonify({
            "status": 'failed',
            'error': 500,
            "message": "Internal server error"
        }), 500
