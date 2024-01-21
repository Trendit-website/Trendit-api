from flask import Flask, jsonify
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from celery import Celery

from app.models.user import Trendit3User
from app.models.role import create_roles
from app.models.item import Item
from app.models.task import Task, AdvertTask, EngagementTask

from config import Config
from app.extensions import db, celery, mail
from app.utils.helpers.basic_helpers import console_log

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app) # changed from db = SQLAlchemy(app)
    mail.init_app(app) # Initialize Flask-Mail
    migrate = Migrate(app, db)
    
    # Initialize Celery
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(result_backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.broker_connection_retry_on_startup = True
    
    console_log('CELERY_BROKER_URL', app.config['CELERY_BROKER_URL'])
    console_log('CELERY_RESULT_BACKEND', app.config['CELERY_RESULT_BACKEND'])
    
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
    
    
    # Setup the Flask-JWT-Extended extension
    jwt = JWTManager(app)
    
    
    # Register blueprints
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    from app.routes.api_admin import bp as api_admin_bp
    app.register_blueprint(api_admin_bp)
    
    from app.routes.error_handlers import bp as errorHandler_bp
    app.register_blueprint(errorHandler_bp)
    
    
    with app.app_context():
        create_roles()  # Create roles for trendit3
    
    @app.route("/test", methods=['PUT'])
    def update_platform_to_lowercase():
        try:
            tasks = Task.query.all()
            for task in tasks:
                task.total_success = 0
                task.total_allocated = 0
            db.session.commit()
            
            return jsonify({
                "status": 'done',
                'message': 'Updated',
                'status code': 200,
            }), 200
        except Exception as e:
            return jsonify({
                "status": 'failed',
                'message': f'Error updating {e}',
                'status code': 401,
            }), 401
    
    return app
