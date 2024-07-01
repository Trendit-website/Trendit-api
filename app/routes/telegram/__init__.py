'''
This package contains the in-house Telegram API webhook routes for the Trendit³ Flask application.

A Flask blueprint named 'telegram_bp' is created to group these routes, and it is registered under the '/api/telegram' URL prefix.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask import Blueprint

telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')

from . import (social_profiles, tasks)
