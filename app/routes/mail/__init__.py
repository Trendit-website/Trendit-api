'''
This package contains the routes to test the HTML email templates

A Flask blueprint named 'mail' is created to group these routes.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from flask import Blueprint, render_template

mail_bp = Blueprint('mail', __name__, url_prefix='/mail')

@mail_bp.route("/welcome", methods=['GET'])
def welcome():
    return render_template('email/welcome.html')

@mail_bp.route("/verify-mail", methods=['GET'])
def verify_mail():
    return render_template('email/verify_email2.html')

@mail_bp.route("/task_rejected", methods=['GET'])
def task_rejected():
    return render_template('email/task_rejected.html')

@mail_bp.route("/task_approved", methods=['GET'])
def task_approved():
    return render_template('email/task_approved.html')

@mail_bp.route("/verify-email", methods=['GET'])
def verify_email():
    return render_template('email/verify_email.html')