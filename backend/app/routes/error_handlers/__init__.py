from flask import Blueprint

bp = Blueprint('errorHandlers', __name__)

from app.routes.error_handlers import handlers
