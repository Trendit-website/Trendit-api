"""
This module defines helper functions for generating HTTP responses in the Trendit³ Flask application.

These functions assist with tasks such as generating success and error responses.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³

@app/utils/helpers/response_helpers.py
"""
from flask import jsonify, make_response, Response

def error_response(msg: str, status_code: int, extra_data: dict | None = None) -> Response:
    '''
    Creates a JSON response for an error with a specified status code.

    Args:
        msg (str): The error message to include in the response.
        status_code (int): The HTTP status code for the response.
        extra_data (dict, optional): Additional data to include in the response. Defaults to None.

    Returns:
        flask.Response: A JSON response object with the error details and status code.
    '''
    response: dict = {
        'status': 'failed',
        'status_code': status_code,
        'message': msg
    }
    if extra_data:
        response.update(extra_data)
    
    response: Response = make_response(response)
    response.status_code = status_code
    
    return response

def success_response(msg: str, status_code: int, extra_data: dict | None = None) -> Response:
    '''
    Creates a JSON response for a success with a specified status code.

    Args:
        msg (str): The success message to include in the response.
        status_code (int): The HTTP status code for the response.
        extra_data (dict, optional): Additional data to include in the response. Defaults to None.

    Returns:
        flask.Response: A JSON response object with the success message and status code.
    '''
    response: dict = {
        'status': 'success',
        'status_code': status_code,
        'message': msg
    }
    if extra_data:
        response.update(extra_data)
    
    response: Response = make_response(response)
    response.status_code = status_code
    
    return response