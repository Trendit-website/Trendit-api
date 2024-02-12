'''
This module defines helper functions for handling bank-related operations in the Trendit³ Flask application.

These functions assist with tasks such as:
    * retrieving a list of banks
    * creating a mapping of bank names to their codes
    * getting the code of a bank given its name.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import requests, logging
from flask import json
from flask_jwt_extended import get_jwt_identity

from app.utils.helpers.basic_helpers import console_log, generate_random_string
from config import Config

def get_banks(country=None):
    url = f"{Config.PAYSTACK_BANKS_URL}?country={country}" if country else Config.PAYSTACK_BANKS_URL
    headers = {
        "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
        "Content-Type": "application/json"
    }
    request_response = requests.get(url, headers=headers)
    return request_response.json()

# This will give you a dictionary mapping bank names to their codes
def create_bank_name_to_code_mapping(country=None):
    banks = get_banks(country)
    mapping = {bank['name']: bank['code'] for bank in banks['data']}
    
    return mapping


def get_bank_code(bank_name, country=None):
    bank_name_to_code_mapping = create_bank_name_to_code_mapping(country)
    return bank_name_to_code_mapping.get(bank_name)
