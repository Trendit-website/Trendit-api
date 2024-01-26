from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

from . import auth, payment, items, item_interactions, location, task, task_performance, profile, referral, religions