import logging, requests
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from ...models import Trendit3User
from ...utils.payments.flutterwave import get_banks, get_bank_code, flutterwave_verify_bank_account
from ...utils.helpers.basic_helpers import log_exception
from ...utils.helpers.response_helpers import error_response, success_response


@api.route("/banks", methods=['GET'])
@jwt_required()
def supported_banks():
    """
    Get a list of all supported banks.

    Returns:
        JSON response with a list of banks and their details.
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = Trendit3User.query.get(current_user_id)
        if user is None:
            return error_response('User not found', 404)
        
        country = user.address.country or 'Nigeria'
        
        banks = get_banks(country)
        
        extra_data = { 'supported_banks': banks[:100] }
        api_response = success_response('supported banks fetched successfully', 200, extra_data)
    except requests.exceptions.RequestException as e:
        log_exception("A RequestException fetching banks from payment gateway", e)
        api_response = error_response(f'An unexpected error occurred fetching banks: {str(e)}', 500)
    except Exception as e:
        log_exception("An exception occurred fetching banks", e)
        api_response = error_response(f'An unexpected error occurred fetching banks: {str(e)}', 500)
    
    return api_response



@api.route("/banks/verify/account", methods=['GET'])
@jwt_required()
def verify_bank_account():
    try:
        data = request.get_json()
        
        account_no = data.get('account_no')
        bank_name = data.get('bank_name')
        bank_code = get_bank_code(bank_name)
        
        account_info = flutterwave_verify_bank_account(account_no, bank_code)
        
        api_response = success_response("account verified", 200, {"account_info": account_info})
    except requests.exceptions.RequestException as e:
        log_exception("RequestException verifying bank account", e)
        api_response = error_response(f"Request Failed: {str(e)}", 500)
    except Exception as e:
        api_response = error_response("An unexpected error occurred verifying bank account", 500)
        log_exception("An exception occurred verifying bank account", e)
    
    return api_response