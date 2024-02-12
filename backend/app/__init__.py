'''
Application factory for Trendit³ API

It sets up and configures the Flask application, initializes various Flask extensions,
sets up CORS, configures logging, registers blueprints and defines additional app-wide settings.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
@Copyright © 2024 Emmanuel Olowu
'''

from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery

from app.models.user import Trendit3User
from app.models.role import create_roles
from app.models.item import Item
from app.models.task import Task, AdvertTask, EngagementTask
from .models.payment import Payment, Transaction, PaystackTransaction, Wallet, Withdrawal

from .jobs import celery_app
from .extensions import db, mail, limiter
from .utils.helpers import check_emerge
from config import Config, configure_logging, config_by_name

def create_app(config_name=Config.ENV):
    '''
    Creates and configures the Flask application instance.

    Args:
        config_class: The configuration class to use (Defaults to Config).

    Returns:
        The Flask application instance.
    '''
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize Flask extensions here
    db.init_app(app)
    mail.init_app(app) # Initialize Flask-Mail
    limiter.init_app(app) # initialize rate limiter
    migrate = Migrate(app, db)
    
    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resources={r"/*": {"origins": Config.CLIENT_ORIGINS}}, supports_credentials=True)

    
    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    # Configure logging
    configure_logging(app)
    
    # Setup the Flask-JWT-Extended extension
    jwt = JWTManager(app)
    
    app.before_request(check_emerge)
    
    # Register blueprints
    from app.routes.api import api as api_bp
    app.register_blueprint(api_bp)
    
    from app.routes.api_admin import bp as api_admin_bp
    app.register_blueprint(api_admin_bp)
    
    from app.error_handlers import bp as errorHandler_bp
    app.register_blueprint(errorHandler_bp)
    
    from app.utils.debugging import debugger as debugger_bp
    app.register_blueprint(debugger_bp)
    
    
    with app.app_context():
        create_roles()  # Create roles for trendit3
    
    
    return app
