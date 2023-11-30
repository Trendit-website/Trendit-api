from flask import request

from app.routes.api import bp
from app.controllers.api import ItemController
from app.utils.helpers.location_helpers import get_naija_states_lga, get_supported_countries, get_supported_country_states


@bp.route('/countries', methods=['GET'])
def get_countries():
    return get_supported_countries()


@bp.route('/states', methods=['GET'])
def get_states():
    country = request.args.get('country', 'nigeria')
    return get_supported_country_states(country)

@bp.route('/nigeria-lga', methods=['GET'])
def naija_states_lga():
    return get_naija_states_lga()