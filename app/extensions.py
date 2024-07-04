'''
This module initializes the extensions used in the Trendit³ Flask application.

It sets up SQLAlchemy, Flask-Mail, and Celery with the configurations defined in the Config class.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)