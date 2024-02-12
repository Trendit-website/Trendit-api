'''
This package register creates the debugging Blueprint.

It includes endpoints for debugging purposes in the Trendit³ Flask application.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from flask import Blueprint

debugger = Blueprint('debuggers', __name__, url_prefix='/debug')

from . import db, health_check, basic