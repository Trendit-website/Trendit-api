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

from ..payments.flutterwave import get_bank_code, create_bank_name_to_code_mapping
