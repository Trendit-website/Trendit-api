'''
This module contains endpoints for debugging operations
related to Trendit³ API Health checks.


@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from flask import Flask, request, current_app
from sqlalchemy import text

from . import debugger
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import log_exception
from config import Config

from ...extensions import db


@debugger.route('/health', methods=['GET'])
def health_check():
    current_app.logger.debug(request)
    return 'Logged debug information', 200

# Database Health Check Endpoint
@debugger.route('/health/db')
def db_health_check():
    try:
        # Ping the database to check the connection status
        result = db.session.execute(text('SELECT 1'))
        current_app.logger.debug(result)
        log_exception('Ping', result)
        db.session.commit()
        return success_response('Okay: Database is reachable', 200)
    except Exception as e:
        log_exception('error', e)
        return error_response(f'Error: {str(e)}', 500)


# External Service Health Check Endpoint
@debugger.route('/health/paystack')
def paystack_service_health_check():
    try:
        import requests
        response = requests.get(Config.PAYSTACK_API_URL)
        log_exception('Response', response)
        
        response.raise_for_status()  # Raise an error for non-200 status codes
        return success_response('Okay', 200)
    except requests.RequestException as e:
        return error_response(str(e), 500)