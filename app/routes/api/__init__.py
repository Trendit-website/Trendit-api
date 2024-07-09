'''
This package contains the API routes for the Trendit³ Flask application.

It includes routes for authentication, payments, items, item interactions, location, task, task performance, profile, referral, religions, stats, and banks.

A Flask blueprint named 'api' is created to group these routes, and it is registered under the '/api' URL prefix.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask import Blueprint, render_template

api = Blueprint('api', __name__, url_prefix='/api')

from . import (error_handlers, auth, payment, items, item_interactions, location, social_profile, social_platforms, task, task_performance, profile, referral, religions, stats, banks, notification, settings, transactions, social_auth, pricing, task_option)

@api.route("/", methods=['GET'])
def index():
    return render_template('api/index.jinja-html')