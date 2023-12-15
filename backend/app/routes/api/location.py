from flask import request

from app.routes.api import bp
from app.controllers.api import LocationController


@bp.route('/countries', methods=['GET'])
def get_countries():
    return LocationController.get_supported_countries()


@bp.route('/states', methods=['GET'])
def get_states():
    country = request.args.get('country', 'nigeria')
    return LocationController.get_supported_country_states(country)

@bp.route('/states/lga/<state>', methods=['GET'])
def naija_states_lga(state):
    return LocationController.get_naija_state_lga(state)
