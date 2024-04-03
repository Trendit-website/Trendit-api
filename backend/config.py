'''
This module defines the configuration settings for the Trendit³ Flask application.

It includes configurations for the environment, database, JWT, Paystack, mail, Cloudinary, and Celery. 
It also includes a function to configure logging for the application.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import os, secrets, logging
from datetime import timedelta
from celery import Celery



class Config:
    # other app configurations
    ENV = os.environ.get('ENV') or 'development'
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:zeddy@localhost:5432/trendit3'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = (ENV == 'development')  # Enable debug mode only in development
    STATIC_DIR = 'app/static'
    UPLOADS_DIR = 'app/static/uploads'
    EMERGENCY_MODE = os.environ.get('EMERGENCY_MODE') or False
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME') or 'https://www.trendit3.com'
    API_DOMAIN_NAME = os.environ.get('API_DOMAIN_NAME') or 'https://api.trendit3.com'
    CLIENT_ORIGINS = os.environ.get('CLIENT_ORIGINS') or 'http://localhost:3000,http://localhost:5173,https://trendit3.vercel.app'
    CLIENT_ORIGINS = [origin.strip() for origin in CLIENT_ORIGINS.split(',')]
    
    # Constants
    TASKS_PER_PAGE = os.environ.get('TASKS_PER_PAGE') or 10
    ITEMS_PER_PAGE = os.environ.get('ITEMS_PER_PAGE') or 10
    PAYMENT_TYPES = ['task-creation', 'membership-fee', 'credit-wallet', 'item-upload']
    
    # JWT configurations
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "super-secret" # Change This
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    
    
    # Paystack Configurations
    PAYMENT_GATEWAY = 'Paystack'
    PAYSTACK_API_URL = os.environ.get('PAYSTACK_API_URL') or "https://api.paystack.co"
    PAYSTACK_INITIALIZE_URL = os.environ.get('PAYSTACK_INITIALIZE_URL') or "https://api.paystack.co/transaction/initialize"
    PAYSTACK_RECIPIENT_URL = os.environ.get('PAYSTACK_RECIPIENT_URL') or "https://api.paystack.co/transferrecipient"
    PAYSTACK_TRANSFER_URL = os.environ.get('PAYSTACK_RECIPIENT_URL') or "https://api.paystack.co/transfer"
    PAYSTACK_COUNTIES_URL = os.environ.get('PAYSTACK_COUNTIES_URL') or "https://api.paystack.co/country"
    PAYSTACK_STATES_URL = os.environ.get('PAYSTACK_STATES_URL') or "https://api.paystack.co/address_verification/states"
    PAYSTACK_BANKS_URL = os.environ.get('PAYSTACK_BANKS_URL') or "https://api.paystack.co/bank"
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY') or "sk_test_a8784e4f50809b0ee5cba711046090b0df20d413"
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY') or "pk_test_b6409653e947befe40cbacc78f7338de0e0764c3"
    
    '''
    # mail configurations
    MAIL_SERVER = 'smtp.hostinger.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'support@trendit3.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    '''
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'olowu2018@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'doyi bkzc mcpq cvcv'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Cloudinary configurations
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') or "dcozguaw3"
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') or "798295575458768"
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET') or "HwXtPdaC5M1zepKZUriKCYZ9tsI"
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'


    # Google config
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # Facebook config
    FB_CLIENT_ID = os.environ.get('FB_CLIENT_ID')
    FB_CLIENT_SECRET = os.environ.get('FB_CLIENT_SECRET')
    FB_REDIRECT_URI = os.environ.get('FB_REDIRECT_URI')

    # TikTok config


class DevelopmentConfig(Config):
    FLASK_DEBUG = True
    DEBUG_TOOLBAR = True  # Enable debug toolbar
    EXPOSE_DEBUG_SERVER = False  # Do not expose debugger publicly

class ProductionConfig(Config):
    DEBUG = False
    FLASK_DEBUG = False
    DEBUG_TOOLBAR = False
    EXPOSE_DEBUG_SERVER = False

# Map config based on environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

def configure_logging(app):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)  # Set the desired logging level
