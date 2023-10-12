import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


## postgresql://postgres:zeddy@localhost:5432/robin_sale
class Config:
    # other app configurations
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')\
        or 'postgresql://postgres:zeddy@localhost:5432/trendit3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_DIR = 'app/static'
    UPLOADS_DIR = 'app/static/uploads'
    
    # JWT configurations
    JWT_SECRET_KEY = "super-secret" # Change This
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in a production environment
    JWT_ACCESS_COOKIE_PATH = '/api/'
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    JWT_COOKIE_CSRF_PROTECT = True
    
    # Paystack configurations
    PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"
    PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"
    PAYSTACK_SECRET_KEY = "sk_test_0e1d695081997b4bee609e4e65cc01155a1b522d"
    PAYSTACK_PUBLIC_KEY = "pk_test_13220295e2a9bd77ce8e5e57d8fbe5803600c4ea"
    
    # mail configurations
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'olowu2018@gmail.com'
    MAIL_PASSWORD = 'doyi bkzc mcpq cvcv'
