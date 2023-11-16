import requests
from flask import jsonify

from app.utils import AppJSON
from app.utils.helpers.basic_helpers import console_log


def get_currency_info(country):
    try:
        response = requests.get(f'https://restcountries.com/v3/name/{country}?fullText=true')
        response.raise_for_status()  # raise an exception if the request failed
        data = response.json()
        
        currency_data = data[0]['currencies']
        
        # Extract the currency code, name, and symbol
        currency_code = list(currency_data.keys())[0]  # Get the first currency code
        currency_name = currency_data[currency_code]['name']
        currency_symbol = currency_data[currency_code]['symbol']
        
        currency_info = {
            'code': currency_code,
            'name': currency_name,
            'symbol': currency_symbol
        }
        
        return currency_info
    except requests.exceptions.RequestException as e:
        console_log('Request failed', str(e))
    except IndexError:
        console_log('IndexError', 'Country not found')
    except Exception as e:
        console_log('An error occurred', str(e))

    return None  # Return None if there was an error


def get_currency_code(country):
    try:
        currency_info = get_currency_info(country)
        
        return currency_info['code']
    except requests.exceptions.RequestException as e:
        console_log('Request failed', e)
    except IndexError:
        console_log('IndexError', 'Country not found')
    except Exception as e:
        console_log('An error occurred', e)

    return None  # Return None if there was an error


def get_naija_states_lga():
    return jsonify(AppJSON.naija_states)