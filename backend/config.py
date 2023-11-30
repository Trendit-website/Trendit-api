import os, secrets
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # other app configurations
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:zeddy@localhost:5432/trendit3'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://trendit3_user:WXyn8pubfYkYkG5pwuTHwCDDIZR7b3Bp@dpg-ckmg2qqv7m0s739krnvg-a.oregon-postgres.render.com/trendit3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_DIR = 'app/static'
    UPLOADS_DIR = 'app/static/uploads'
    DOMAIN_NAME = 'www.trendit3.com'
    CLIENT_ORIGIN = os.environ.get('CLIENT_ORIGIN') or 'http://localhost:3000'
    TASKS_PER_PAGE = os.environ.get('TASKS_PER_PAGE') or 10
    ITEMS_PER_PAGE = os.environ.get('ITEMS_PER_PAGE') or 10
    
    # JWT configurations
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "super-secret" # Change This
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in a production environment
    JWT_ACCESS_COOKIE_PATH = '/api/'
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    JWT_COOKIE_CSRF_PROTECT = True
    
    # Paystack Configurations
    PAYSTACK_API_URL = os.environ.get('PAYSTACK_API_URL') or "https://api.paystack.co"
    PAYSTACK_INITIALIZE_URL = os.environ.get('PAYSTACK_INITIALIZE_URL') or "https://api.paystack.co/transaction/initialize"
    PAYSTACK_COUNTIES_URL = os.environ.get('PAYSTACK_COUNTIES_URL') or "https://api.paystack.co/country"
    PAYSTACK_STATES_URL = os.environ.get('PAYSTACK_STATES_URL') or "https://api.paystack.co/address_verification/states"
    PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY') or "sk_test_a8784e4f50809b0ee5cba711046090b0df20d413"
    PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY') or "pk_test_b6409653e947befe40cbacc78f7338de0e0764c3"
    
    # mail configurations
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'olowu2018@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'doyi bkzc mcpq cvcv'
    
    # Cloudinary configurations
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') or "dcozguaw3"
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') or "798295575458768"
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET') or "HwXtPdaC5M1zepKZUriKCYZ9tsI"
