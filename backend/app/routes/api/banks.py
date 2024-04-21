import logging, requests
from flask import request, jsonify

from . import api
from ...utils.payments.flutterwave import get_banks
from ...utils.helpers.basic_helpers import log_exception
from ...utils.helpers.response_helpers import error_response, success_response


# RELIGIONS ENDPOINTS
@api.route("/supported-banks", methods=['GET'])
def supported_banks():
    """
    Get a list of all supported banks.

    Returns:
        JSON response with a list of banks and their details.
    """
    try:
        banks = get_banks()
        
        extra_data = { 'supported_banks': banks }
        api_response = success_response('supported banks fetched successfully', 200, extra_data)
    except requests.exceptions.RequestException as e:
        log_exception("A RequestException fetching banks from payment gateway", e)
        api_response = error_response(f'An unexpected error occurred fetching banks: {str(e)}', 500)
    except Exception as e:
        log_exception("An exception occurred fetching banks", e)
        api_response = error_response(f'An unexpected error occurred fetching banks: {str(e)}', 500)
    
    return api_response


