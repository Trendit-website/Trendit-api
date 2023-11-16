from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.models.user import Trendit3User
from app.models.item import Item
from app.models.task import Task, AdvertTask, EngagementTask
from app.utils.helpers.location_helpers import get_currency_code, get_currency_info
from app.utils.helpers.basic_helpers import console_log

from config import Config
from app.extensions import db
from app.extensions import mail

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app) # changed from db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Set up CORS. Allow '*' for origins.
    cors = CORS(app, resources = {r"/*":{"origins": "*"}})

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
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Register blueprints
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    from app.routes.error_handlers import bp as errorHandler_bp
    app.register_blueprint(errorHandler_bp)
    
    @app.route("/test", methods=['GET'])
    def test():
        
        task = Task.query.filter_by(id=2).first()
        console_log('task', task)
        key = getattr(task, 'platformx')
        console_log('key', key)
                    
        
        if task is None:
            return key
        else:
            return 'no task'
    
    return app
