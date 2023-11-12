# app/utils/helpers/response_helpers.py

from flask import jsonify

def error_response(msg, status_code, extra_data=None):
    response = {
        'status': 'failed',
        'status_code': status_code,
        'message': msg
    }
    if extra_data:
        response.update(extra_data)
    
    return jsonify(response), status_code

def success_response(msg, status_code, extra_data=None):
    response = {
        'status': 'success',
        'status_code': status_code,
        'message': msg
    }
    if extra_data:
        response.update(extra_data)
    
    return jsonify(response), status_code