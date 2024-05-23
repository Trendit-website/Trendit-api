'''
This module defines the controller methods for pricing in the Trendit³ Flask application.

It includes methods for getting prices, adding pricing, updating pricing and deleting pricing.

@author: Chris
@link: https://github.com/al-chris
@package: Trendit³
'''

from flask import request

from ...extensions import db
from ...models import Pricing, PricingCategory
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
                    "description": item.description,
                    "category": item.category.value,
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
        
    @staticmethod
    def add_pricing():
        try:
            data = request.get_json()
            item_name = data.get('item_name')
            price_pay = data.get('price_pay')
            price_earn = data.get('price_earn')
            price_category = data.get('category')
            price_description = data.get('price_description')

            if not item_name or not price_pay or not price_earn or not price_description:
                return error_response('Item name, price_pay, price_description and price_earn are required', 400)

            pricing = Pricing(item_name=item_name, price_pay=price_pay, price_earn=price_earn, price_category=PricingCategory[price_category], description=price_description)
            db.session.add(pricing)
            db.session.commit()
            db.session.close()

            return success_response('Pricing added successfully', 201)
        
        except Exception as e:
            console_log("An error occurred while adding pricing", e)
            return error_response('An error occurred while adding pricing', 500)
        
    @staticmethod
    def update_pricing():
        try:
            data = request.get_json()
            item_name = data.get('item_name')
            price_pay = data.get('price_pay')
            price_earn = data.get('price_earn')
            price_category = data.get('category')
            price_description = data.get('price_description')

            if not item_name:
                return error_response('Item name and price are required', 400)

            pricing = Pricing.query.filter_by(item_name=item_name).first()

            if not pricing:
                return error_response('Pricing not found', 404)
            
            if price_pay:
                pricing.price_pay = price_pay

            if price_earn:
                pricing.price_earn = price_earn                

            if price_description:
                pricing.description = price_description

            if price_category in [cat.value for cat in list(PricingCategory)]:
                pricing.category = PricingCategory[price_category]

            db.session.commit()
            
            db.session.close()

            return success_response('Pricing updated successfully', 200)
        
        except Exception as e:
            console_log("An error occurred while updating pricing", e)
            return error_response('An error occurred while updating pricing', 500)
        
    @staticmethod
    def delete_pricing():
        try:
            data = request.get_json()
            item_name = data.get('item_name')

            if not item_name:
                return error_response('Item name is required', 400)

            pricing = Pricing.query.filter_by(item_name=item_name).first()

            if not pricing:
                return error_response('Pricing not found', 404)

            db.session.delete(pricing)
            db.session.commit()
            db.session.close()

            return success_response('Pricing deleted successfully', 200)
        
        except Exception as e:
            console_log("An error occurred while deleting pricing", e)
            return error_response('An error occurred while deleting pricing', 500)