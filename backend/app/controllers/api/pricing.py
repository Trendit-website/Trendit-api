'''
This module defines the controller method for pricing in the Trendit³ Flask application.

It includes method for getting all prices.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''


from ...extensions import db
from ...models import Pricing
from ...utils.helpers.basic_helpers import console_log
from ...utils.helpers.response_helpers import error_response, success_response


class PricingController:
    @staticmethod
    def get_all_pricing():
        try:
            pricings = Pricing.query.all()

            prices = []

            for item in pricings:
                price = {
                    "item_name": item.item_name,
                    "price_earn": item.price_earn,
                    "price_pay": item.price_pay,
                    "created_at": str(item.created_at),  # Convert to string
                    "updated_at": str(item.updated_at)  # Convert to string
                }

                prices.append(price)

            extra_data = {'pricing': prices}

            db.session.close()

            return success_response('Pricing retrieved successfully', 200, extra_data=extra_data)
        
        except Exception as e:
            console_log("An error occurred while retrieving pricing", e)
            return error_response('An error occurred while retrieving pricing', 500)
        