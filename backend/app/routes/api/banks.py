import logging
from flask import request, jsonify

from . import api
from ...utils.helpers.bank_helpers import get_banks
from ...utils.helpers.response_helpers import error_response, success_response


# RELIGIONS ENDPOINTS
@api.route("/supported-banks", methods=['GET'])
def supported_banks():
    """
    Get a list of all supported banks.

    Returns:
        JSON response with a list of banks and their details.
    """
    error = False
    try:
        banks = get_banks()
        
        extra_data = {
            'supported_banks': banks['data']
        }
    except Exception as e:
        error = True
        status_code = 500
        msg = f'An error occurred while processing the request: {str(e)}'
        logging.exception(f"An exception occurred during fetching payment history: \n  {str(e)}")
    if error:
        return error_response(msg, status_code)
    else:
        return success_response('supported banks fetched successfully', 200, extra_data)


