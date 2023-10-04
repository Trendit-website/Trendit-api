from flask import Blueprint

bp = Blueprint('payment', __name__)

from app.routes.payment import payment