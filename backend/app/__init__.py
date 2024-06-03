'''
Application factory for Trendit³ API

It sets up and configures the Flask application, initializes various Flask extensions,
sets up CORS, configures logging, registers blueprints and defines additional app-wide settings.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
@Copyright © 2024 Emmanuel Olowu
'''

from flask import Flask, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from celery import Celery

from app.models.user import Trendit3User
from app.models.role import create_roles
from app.models.item import Item
from app.models.task import Task, AdvertTask, EngagementTask
from .models.payment import Payment, Transaction, Wallet, Withdrawal

from .jobs import celery_app
from .extensions import db, mail, limiter
from .utils.helpers.basic_helpers import log_exception
from .utils.helpers.user_helpers import add_user_role
from .utils.middleware import set_access_control_allows, check_emerge, json_check, ping_url
from config import Config, configure_logging, config_by_name, block_postman

def create_app(config_name=Config.ENV):
    '''
    Creates and configures the Flask application instance.

    Args:
        config_name: The configuration class to use (Defaults to Config).

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
    jwt = JWTManager(app) # Setup the Flask-JWT-Extended extension
    
    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resources={r"/*": {"origins": Config.CLIENT_ORIGINS}}, supports_credentials=True)

    # Use the after_request decorator to set Access-Control-Allow
    app.after_request(set_access_control_allows)
    
    # Before request hooks
    app.before_request(check_emerge)
    #app.before_request(ping_url)
    # app.before_request(json_check)
    
    
    # Block Postman requests in production
    if app.config['ENV'] == 'production':
        app.before_request(block_postman)
    
    # Configure logging
    configure_logging(app)
    
    
    # Register blueprints
    from .routes.main import main
    app.register_blueprint(main)
    
    from .routes.api import api as api_bp
    app.register_blueprint(api_bp)
    
    from .routes.api_admin import bp as api_admin_bp
    app.register_blueprint(api_admin_bp)
    
    from .error_handlers import bp as errorHandler_bp
    app.register_blueprint(errorHandler_bp)
    
    from .utils.debugging import debugger as debugger_bp
    app.register_blueprint(debugger_bp)


    # Swagger setup
    SWAGGER_URL = '/api/docs'
    API_URL = 'http://petstore.swagger.io/v2/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Trendit³ API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route('/spec')
    def spec():
        swag = swagger(app)
        swag['info']['title'] = "Your API"
        swag['info']['description'] = "API documentation"
        swag['info']['version'] = "1.0.0"
        return jsonify(swag)
    
    
    with app.app_context():
        create_roles()  # Create roles for trendit3
    
    return app
