from app.routes.api import bp
from app.controllers.api import ItemController
from app.utils.helpers.lga import get_naija_states_lga

@bp.route('/naija-states-lga', methods=['GET'])
def naija_states_lga():
    return get_naija_states_lga()