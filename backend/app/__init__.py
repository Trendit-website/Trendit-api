import time, requests
from uuid import uuid4
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
from .models.payment import Payment, Transaction, PaystackTransaction, Wallet, Withdrawal

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
            print('fetching payments...')
            payments = Payment.query.all()
            time.sleep(2)
            print('updating each payment record...')
            for payment in payments:
                print(f'updating task {payment.id}...')
                if payment.payment_method == 'payment_gateway':
                    payment.payment_method = Config.PAYMENT_GATEWAY.lower()
                payment.key = uuid4()
                print(f'UUID {payment.key}...')
                time.sleep(1)
            
            print('fetching transactions...')
            transactions = Transaction.query.all()
            time.sleep(1)
            print('updating each transactions...')
            for transaction in transactions:
                print(f'updating transaction {transaction.id}...')
                transaction.amount = 0
                for payment in payments:
                    if transaction.payment_type == 'task_creation' and transaction.status.lower() == 'complete' and payment.payment_type == 'task_creation':
                        transaction.amount = payment.amount
                    
                    if transaction.payment_type == 'credit-wallet' and transaction.status.lower() == 'complete' and payment.payment_type == 'credit-wallet':
                        transaction.amount = payment.amount
                    
                    if transaction.payment_type == 'membership-fee' and transaction.status.lower() == 'complete' and payment.payment_type == 'membership-fee':
                        transaction.amount = payment.amount
                
                user = Trendit3User.query.filter(Trendit3User.id == transaction.user_id).first()
                transaction.trendit3_user = user
                transaction.transaction_type = 'payment'
                
                reference = transaction.tx_ref
                auth_headers = {
                    "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
                    "Content-Type": "application/json"
                }
                paystack_response = requests.get('https://api.paystack.co/transaction/verify/{}'.format(reference), headers=auth_headers)
                verification_response = paystack_response.json()
                
                
                if verification_response['status'] is False:
                    print(verification_response['message'], 404)
                    raise Exception
                
                print('UPDATING PAYSTACK TRANSACTION...')
                transaction.amount = int(verification_response['data']['amount'])/100
                paystack_transaction = PaystackTransaction(trendit3_user=user, tx_ref=reference, payment_type=transaction.payment_type, status=transaction.status, amount=int(verification_response['data']['amount'])/100, created_at=verification_response['data']['created_at'])
        
                db.session.add(paystack_transaction)
            
            
            db.session.commit()
            print('update for each payments is Done')
        except Exception as e:
            print(f'Error updating each payments: ==> {e}')
        
    
    return app
