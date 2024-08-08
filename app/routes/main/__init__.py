'''
This package contains the main routes for the Trendit³ Flask application.

A Flask blueprint named 'main' is created to group these routes.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=['GET'])
def index():
    return render_template('api/index.jinja-html')