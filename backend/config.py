import os, secrets, logging
from datetime import timedelta
from celery import Celery

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # other app configurations
    ENV = 'development'
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:zeddy@localhost:5432/trendit3'
    
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://trendit3user:F1dIvuYINM5EJZiF7Vdlpzr0aPafLzVX@dpg-clq5ihhjvg7s73e3amig-a.oregon-postgres.render.com/trendit_db_vhh7'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_DIR = 'app/static'
    UPLOADS_DIR = 'app/static/uploads'
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME') or 'www.trendit3.com'
    TASKS_PER_PAGE = os.environ.get('TASKS_PER_PAGE') or 10
    ITEMS_PER_PAGE = os.environ.get('ITEMS_PER_PAGE') or 10
    CLIENT_ORIGINS = os.environ.get('CLIENT_ORIGINS') or 'http://localhost:3000,http://localhost:5173,https://trendit3.vercel.app'
    CLIENT_ORIGINS = [origin.strip() for origin in CLIENT_ORIGINS.split(',')]
    
    # JWT configurations
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "super-secret" # Change This
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    
    
    # Paystack Configurations
    PAYMENT_GATEWAY = 'Paystack'
    PAYSTACK_API_URL = os.environ.get('PAYSTACK_API_URL') or "https://api.paystack.co"
    PAYSTACK_INITIALIZE_URL = os.environ.get('PAYSTACK_INITIALIZE_URL') or "https://api.paystack.co/transaction/initialize"
    PAYSTACK_COUNTIES_URL = os.environ.get('PAYSTACK_COUNTIES_URL') or "https://api.paystack.co/country"
    PAYSTACK_STATES_URL = os.environ.get('PAYSTACK_STATES_URL') or "https://api.paystack.co/address_verification/states"
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
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'olowu2018@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'doyi bkzc mcpq cvcv'
    
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

    @classmethod
    def init_celery(cls):
        app = Celery('app', broker=cls.CELERY_BROKER_URL, backend=cls.CELERY_RESULT_BACKEND)
        return app
    

def configure_logging(app):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)  # Set the desired logging level

