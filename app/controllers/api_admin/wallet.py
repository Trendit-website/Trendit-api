import requests
from sqlalchemy.exc import ( DataError, DatabaseError )


from ...extensions import db
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import log_exception, console_log
from ...utils.payments.flutterwave import flutterwave_fetch_balance


class AdminWalletController:

    @staticmethod
    def get_wallet_balance():
        try:
            balances = flutterwave_fetch_balance()
            
            if balances is None:
                return error_response("unable to fetch wallet ballance", 500)
            
            extra_data={"balances": balances}
            
            api_response = success_response("balance fetched successfully", 200, extra_data)
        except requests.exceptions.RequestException as e:
            log_exception("A RequestException occurred fetching flutterwave balance", e)
            api_response = error_response("Error connecting to payment gateway", 500)
        except (DataError, DatabaseError) as e:
            log_exception(f"An exception occurred during database operation:", e)
            api_response = error_response("Database error occurred", 500)
        except Exception as e:
            log_exception(f"An unexpected exception occurred fetching flutterwave balance", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response

