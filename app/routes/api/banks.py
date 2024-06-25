import logging, requests
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from ...models import Trendit3User
from ...utils.payments.flutterwave import get_banks, get_bank_code, flutterwave_verify_bank_account
from ...utils.helpers.basic_helpers import log_exception, console_log
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
        
        extra_data = { 'supported_banks': banks }
        api_response = success_response('supported banks fetched successfully', 200, extra_data)
    except requests.exceptions.RequestException as e:
        log_exception("A RequestException fetching banks from payment gateway", e)
        api_response = error_response(f'An unexpected error occurred fetching banks: {str(e)}', 500)
    except Exception as e:
        log_exception("An exception occurred fetching banks", e)
        api_response = error_response(f'An unexpected error occurred fetching banks: {str(e)}', 500)
    
    return api_response



@api.route("/banks/verify/account", methods=['POST'])
@jwt_required()
def verify_bank_account():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        current_user = Trendit3User.query.get(current_user_id)
        if not current_user:
            return error_response(f"user not found", 404)
        
        account_no = data.get('account_no')
        bank_name = data.get('bank_name', '').lower()
        user_country = current_user.address.country
        bank_code = get_bank_code(bank_name, user_country)
        
        if not bank_code:
            return error_response("make sure you selected a valid bank", 400)
        
        account_info = flutterwave_verify_bank_account(account_no, bank_code)
        
        api_response = success_response("account verified", 200, {"account_info": account_info})
    except AttributeError as e:
        log_exception("AttributeError verifying bank account", e)
        api_response = error_response(f"make sure bank name and bank code is provided", 400)
    except requests.exceptions.RequestException as e:
        log_exception("RequestException verifying bank account", e)
        api_response = error_response(f"An unexpected error occurred: {str(e)}", 500)
    except Exception as e:
        api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
        log_exception("An exception occurred verifying bank account", e)
    
    return api_response