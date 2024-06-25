'''
This module contains endpoints for basic debugging operations


@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

import logging, os, platform, json
from datetime import timedelta
from flask import request, current_app

from . import debugger
from ...extensions import limiter
from ...utils.helpers.basic_helpers import log_exception
from ...utils.helpers.response_helpers import error_response, success_response


@debugger.route('/log', methods=['GET'])
def debug_log():
    current_app.logger.debug(request)
    return 'Logged debug information', 200


@debugger.route('/trigger-error', methods=['GET'])
def trigger_error():
    """
    Trigger an intentional error for debugging purposes.

    Returns:
        JSON response: A JSON response indicating that an error has been triggered.
    """
    try:
        # Trigger a KeyError by accessing a non-existent key in a dictionary
        a_dict = {}
        value = a_dict['non_existent_key']
    except Exception as e:
        # Log the error and return a JSON response indicating that an error has been triggered
        log_exception('Error Triggered', e)
        return error_response(f'An error has been triggered for debugging purposes: {str(e)}', 500)


@debugger.route('/env', methods=['GET'])
@limiter.limit("5/minute")
def debug_environment():
    """
    Retrieve information about the environment in which the Flask application is running.

    Returns:
        JSON response: A JSON response containing information about the environment.
    """
    try:
        # Retrieve configuration information from current Flask application
        config_info = {
            key: value.decode('latin-1') if isinstance(value, bytes) else str(value)
            for key, value in current_app.config.items()
        }

        # Retrieve environment variables
        environment_variables = {
            key: value.decode('latin-1') if isinstance(value, bytes) else str(value)
            for key, value in os.environ.items()
        }
        
        # Retrieve system information
        system_info = platform.uname()._asdict()
        for key, value in system_info.items():
            if isinstance(value, timedelta):
                system_info[key] = str(value)
        
        extra_data = {
            'environment_info': {
                'config': config_info,
                'environment_variables': environment_variables,
                'system_info': system_info
            }
        }
        return success_response('environment info fetched', 200, extra_data)
    except Exception as e:
        log_exception('Exception', e)
        return error_response(f'Error: {str(e)}', 500)
