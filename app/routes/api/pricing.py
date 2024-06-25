from . import api
from app.controllers.api.pricing import PricingController

@api.route('/pricing', methods=['GET'])
def get_all_pricing():
    return PricingController.get_all_pricing()
