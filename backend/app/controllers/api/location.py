import requests, logging
from flask import json, request

from config import Config
from ...utils import AppJSON
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response

from ...utils.payments.flutterwave import fetch_supported_countries



class LocationController:
    @staticmethod
    def get_supported_countries():
        
        try:
            supported_countries = fetch_supported_countries()
            if not supported_countries:
                return  error_response('Failed to get fetch supported countries', 500)
            
            supported_countries.insert(0, {"name": "All Countries", "currency_code": "all", "iso_code":"all"})
            extra_data = {
                'countries': supported_countries,
                'total': len(supported_countries)
            }
            
            api_response =  success_response('Countries fetched successfully', 200, extra_data)
        except requests.exceptions.RequestException as e:
            log_exception('Request failed', e)
            api_response =  error_response('Request failed', 500)
        except Exception as e:
            log_exception("An exception occurred getting supported countries.", e)
            api_response =  error_response('Failed to get fetch supported countries', 500)
        
        return api_response


    @staticmethod
    def get_supported_country_states():
        error = False
        
        data = request.get_json()
        country = data.get('country', '')
        if not country:
            return error_response('country name is required', 400)
            
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
                states.insert(0, {"name": "All States", "state_code": "all"})
                
                if country.lower() == "nigeria":
                    plateau_index = next((index for index, state in enumerate(states) if state['name'] == 'Plateau State'), None)
                    states.insert(plateau_index + 1, {"name": "Rivers State", "state_code": "RI"})
                
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
            logging.exception("An exception occurred getting the states of PAYSTACK supported countries.", str(e)) # Log the error details for debugging
        
        if error:
            return error_response(msg, status_code, response_data)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def get_states_cities(state):
        error = False
        
        try:
            pass
        except Exception as e:
            error = True
            msg = 'An error occurred while processing the request.'
            status_code = 500
            logging.exception("An exception occurred getting PAYSTACK supported countries.", str(e)) # Log the error details for debugging
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code)
    
    
    @staticmethod
    def get_naija_state_lga():
        try:
            data = request.get_json()
            state = data.get('state', '')
            if not state:
                return error_response('state is required', 400)
            
            # Add logic to include 'state' if request was sent without 'state' suffix
            if state and not state.lower().endswith(" state"):
                state = state.strip()  # Remove leading/trailing spaces
                state += " state"
            
            # send request
            lga = AppJSON.get_local_governments(state)
            
            if len(lga) <= 1:
                api_response = error_response(f"{state} doesn't have any local government", 400)
                return api_response
            
            extra_data = {
                'total': len(lga),
                'state_lga': lga
            }
            api_response = success_response(f"Local governments for {state} fetched successfully", 200, extra_data)
            
        except Exception as e:
            log_exception("An exception occurred getting Local governments", e)
            api_response = error_response('An error occurred while processing the request.', 500)
        
        return api_response