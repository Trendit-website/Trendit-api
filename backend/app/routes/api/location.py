from flask import request

from . import api
from app.controllers.api import LocationController


@api.route('/countries', methods=['GET'])
def get_countries():
    return LocationController.get_supported_countries()


@api.route('/states', methods=['POST'])
def get_states():
    return LocationController.get_supported_country_states()

@api.route('/states/lga', methods=['POST'])
def naija_states_lga():
    return LocationController.get_naija_state_lga()
