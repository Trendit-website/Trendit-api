'''
This is the entry point of the Trendit³ Flask application.

It creates an instance of the application and runs it.

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''
from app import create_app

app, celery = create_app()
app.app_context().push()