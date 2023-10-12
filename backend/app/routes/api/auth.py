from flask import Flask, jsonify
from app.routes.api import bp
from app.controllers.api.auth import AuthController

@bp.route("/signup", methods=['POST'])
def signUp():
    return AuthController.signUp()

@bp.route("/verify-email", methods=['POST'])
def verify_email():
    return AuthController.verify_email()

@bp.route("/login", methods=['POST'])
def login():
    return AuthController.login()