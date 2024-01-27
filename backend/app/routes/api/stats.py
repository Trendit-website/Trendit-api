from flask import request

from . import api
from ...controllers.api import StatsController


@api.route('/stats', methods=['GET'])
def get_countries():
    return StatsController.get_stats()
