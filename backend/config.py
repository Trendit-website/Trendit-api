import os

basedir = os.path.abspath(os.path.dirname(__file__))


## postgresql://postgres:zeddy@localhost:5432/robin_sale
class Config:
    SECRET_KEY = os.urandom(32)
    JWT_SECRET_KEY = "super-secret" # Change This
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')\
        or 'postgresql://postgres:zeddy@localhost:5432/trendit3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_DIR = 'app/static'
    UPLOADS_DIR = 'app/static/uploads'