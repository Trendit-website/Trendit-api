'''
This module contains the functions for handling conversion rates of currencies

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''

import requests
from cachetools import cached, TTLCache

from config import Config
from ..helpers import console_log

# Create a cache with a Time-To-Live (TTL) of 12 hour (43200 seconds)
cache = TTLCache(maxsize=100, ttl=43200)

@cached(cache)
def fetch_exchange_rates(base_currency="NGN"):
    response = requests.get(f"{Config.EXCHANGE_RATE_API_URL}/{base_currency}")
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("result") == "success":
            return response_data['conversion_rates']
    return None

def convert_amount(balance_in_naira, target_currency):
    exchange_rates = fetch_exchange_rates()
    
    if target_currency in exchange_rates:
        converted_amount = balance_in_naira * exchange_rates[target_currency]
        return round(converted_amount, 2)
    return balance_in_naira  # Default to Naira if no rate is found
