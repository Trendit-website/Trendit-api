import requests, logging
from flask import jsonify, json

from config import Config
from app.utils import AppJSON
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.response_helpers import error_response, success_response


def get_supported_countries():
    error = False
    
    try:
        auth_headers ={
            "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
            "Content-Type": "application/json"
        }
        
        # send request
        response = requests.get(Config.PAYSTACK_COUNTIES_URL, headers=auth_headers)
        response.raise_for_status()  # raise an exception if the request failed
        response_data = json.loads(response.text)
        
        if response_data['status']:
            status_code = 200
            msg = response_data['message']
            countries = response_data['data']
            supported_countries = [{'name': country['name'], 'iso_code': country['iso_code'], 'currency_code': country['default_currency_code']} for country in countries]
            extra_data = {
                'countries': supported_countries,
                'total': len(supported_countries)
            }
        else:
            error = True
            status_code = 400
            msg = response_data['message']
    except requests.exceptions.RequestException as e:
        error = True
        msg = 'Request failed'
        status_code = 500
        console_log('Request failed', str(e))
    except Exception as e:
        error = True
        msg = 'An error occurred while processing the request.'
        status_code = 500
        logging.exception("An exception occurred getting PAYSTACK supported countries.", str(e)) # Log the error details for debugging
    
    if error:
        return error_response(msg, status_code, response_data)
    else:
        return success_response(msg, status_code, extra_data)


def get_supported_country_states(country):
    error = False
    
    # Replace 'Côte d'Ivoire' with 'Ivory Coast'
    if country.lower() == "côte d'ivoire":
        country = "Ivory Coast"
    
    try:
        auth_headers ={
            "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
            "Content-Type": "application/json"
        }
        auth_data = json.dumps({
            "country": country
        })
        
        # send request
        response = requests.post(f'https://countriesnow.space/api/v0.1/countries/states', headers=auth_headers, data=auth_data)
        response_data = json.loads(response.text)
        response.raise_for_status()  # raise an exception if the request failed
        
        if not response_data['error']:
            status_code = 200
            msg = response_data['msg']
            states = response_data['data']['states']
            extra_data = {
                'states': states,
                'total': len(states)
            }
        else:
            error = True
            status_code = 400
            msg = response_data['message']
    except requests.exceptions.RequestException as e:
        error = True
        msg = 'Request failed'
        status_code = 500
        response_data = {} if not response_data else {'message': response_data['msg']}
        console_log('Request failed', str(e))
    except Exception as e:
        error = True
        msg = 'An error occurred while processing the request.'
        status_code = 500
        logging.exception("An exception occurred getting PAYSTACK supported countries.", str(e)) # Log the error details for debugging
    
    if error:
        return error_response(msg, status_code, response_data)
    else:
        return success_response(msg, status_code, extra_data)


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