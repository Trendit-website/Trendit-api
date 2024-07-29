'''
Application factory for Trendit³ API

It sets up and configures the Flask application, initializes various Flask extensions,
sets up CORS, configures logging, registers blueprints and defines additional app-wide settings.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
@Copyright © 2024 Emmanuel Olowu
'''

from flask import Flask, jsonify, request
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from celery import Celery

from .models.user import Trendit3User
from .models.role import create_roles
from .models.item import Item
from .models.task import Task, AdvertTask, EngagementTask
from .models.payment import Payment, Transaction, Wallet, Withdrawal
from .models.notification import Notification, MessageType
from .models.task_option import populate_task_options

from .celery import make_celery
from .extensions import db, mail, limiter
from .utils.helpers.response_helpers import error_response
from .utils.helpers.basic_helpers import log_exception, console_log
from .utils.helpers.user_helpers import add_user_role
from .utils.middleware import set_access_control_allows, check_emerge, json_check, ping_url
from config import Config, configure_logging, config_by_name


def create_app(config_name=Config.ENV):
    '''
    Creates and configures the Flask application instance.

    Args:
        config_name: The configuration class to use (Defaults to Config).

    Returns:
        The Flask application instance.
    '''
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_by_name[config_name])
    
    

    # Initialize Flask extensions here
    db.init_app(flask_app)
    mail.init_app(flask_app) # Initialize Flask-Mail
    limiter.init_app(flask_app) # initialize rate limiter
    migrate = Migrate(flask_app, db)
    jwt = JWTManager(flask_app) # Setup the Flask-JWT-Extended extension
    
    # Set up CORS. Allow '*' for origins.
    cors = CORS(flask_app, resources={r"/*": {"origins": Config.CLIENT_ORIGINS}}, supports_credentials=True)

    # Use the after_request decorator to set Access-Control-Allow
    flask_app.after_request(set_access_control_allows)
    
    # Before request hooks
    flask_app.before_request(check_emerge)
    #flask_app.before_request(ping_url)
    # flask_app.before_request(json_check)
    
    
    # Configure logging
    configure_logging(flask_app)
    
    
    # Register blueprints
    from .routes.main import main
    flask_app.register_blueprint(main)
    
    from .routes.api import api as api_bp
    flask_app.register_blueprint(api_bp)
    
    from .routes.api_admin import bp as api_admin_bp
    flask_app.register_blueprint(api_admin_bp)
    
    from .routes.telegram import telegram_bp
    flask_app.register_blueprint(telegram_bp)
    
    from .routes.mail import mail_bp
    flask_app.register_blueprint(mail_bp)
    
    from .error_handlers import bp as errorHandler_bp
    flask_app.register_blueprint(errorHandler_bp)
    
    from .utils.debugging import debugger as debugger_bp
    flask_app.register_blueprint(debugger_bp)


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
    flask_app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @flask_app.route('/spec')
    def spec():
        swag = swagger(flask_app)
        swag['info']['title'] = "Your API"
        swag['info']['description'] = "API documentation"
        swag['info']['version'] = "1.0.0"
        return jsonify(swag)
    
    
    # Initialize Celery and ensure tasks are imported
    celery = make_celery(flask_app)
    import app.celery.jobs.tasks # Ensure the tasks are imported
    celery.set_default()
    
    
    with flask_app.app_context():
        create_roles()  # Create roles for trendit3
        populate_task_options()
        
        # notifications: list[Notification] = Notification.query.all()
        
        # for notification in notifications:
        #     notification.update(title=notification.body)
    
    return flask_app, celery
