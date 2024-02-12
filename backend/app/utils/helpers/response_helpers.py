'''
This module defines helper functions for generating HTTP responses in the Trendit³ Flask application.

These functions assist with tasks such as generating success and error responses.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³

@app/utils/helpers/response_helpers.py
'''
from flask import jsonify

def error_response(msg, status_code, extra_data=None):
    '''
    Creates a JSON response for an error with a specified status code.

    Args:
        msg (str): The error message to include in the response.
        status_code (int): The HTTP status code for the response.
        extra_data (dict, optional): Additional data to include in the response. Defaults to None.

    Returns:
        flask.Response: A JSON response object with the error details and status code.
    '''
    response = {
        'status': 'failed',
        'status_code': status_code,
        'message': msg
    }
    if extra_data:
        response.update(extra_data)
    
    return jsonify(response), status_code

def success_response(msg, status_code, extra_data=None):
    '''
    Creates a JSON response for a success with a specified status code.

    Args:
        msg (str): The success message to include in the response.
        status_code (int): The HTTP status code for the response.
        extra_data (dict, optional): Additional data to include in the response. Defaults to None.

    Returns:
        flask.Response: A JSON response object with the success message and status code.
    '''
    response = {
        'status': 'success',
        'status_code': status_code,
        'message': msg
    }
    if extra_data:
        response.update(extra_data)
    
    return jsonify(response), status_code