import time
from flask import Flask, jsonify, request
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery

from app.models.user import Trendit3User
from app.models.role import create_roles
from app.models.item import Item
from app.models.task import Task, AdvertTask, EngagementTask

from config import Config, configure_logging
from app.extensions import db, mail
from app.jobs import celery_app
from app.utils.helpers.basic_helpers import console_log

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    mail.init_app(app) # Initialize Flask-Mail
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
    
    
    # Register blueprints
    from app.routes.api import api as api_bp
    app.register_blueprint(api_bp)
    
    from app.routes.api_admin import bp as api_admin_bp
    app.register_blueprint(api_admin_bp)
    
    from app.routes.error_handlers import bp as errorHandler_bp
    app.register_blueprint(errorHandler_bp)
    
    
    with app.app_context():
        create_roles()  # Create roles for trendit3
    
    @app.cli.command()
    def quickUpdate():
        """Update task in database."""
        try:
            print('fetching tasks...')
            tasks = Task.query.all()
            time.sleep(2)
            print('updating each tasks...')
            for task in tasks:
                print(f'updating task {task.id}...')
                task.total_success = 0
                task.total_allocated = 0
                time.sleep(1)
            db.session.commit()
            print('update for each tasks is Done')
        except Exception as e:
            print(f'Error updating each tasks: ==> {e}')
        
    
    return app
