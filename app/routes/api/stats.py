from flask import request
from flask_jwt_extended import jwt_required

from . import api
from ...controllers.api import StatsController


@api.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    return StatsController.get_stats()
