import sys
import logging
from slugify import slugify
from flask import request, Response, redirect, url_for, abort, jsonify
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

from app.extensions import db
from app.models.user import Trendit3User, Address

class AuthController:
    @staticmethod
    def signUp():
        error = False
        
        if request.method == 'POST':
            try:
                data = request.get_json()
                username = data.get('username')
                email = data.get('email')
                gender = data.get('gender')
                country = data.get('country')
                state = data.get('state')
                local_government = data.get('local_government')
                password = data.get('password')
                
                hashedPwd = generate_password_hash(password, "sha256")
                
                newUser = Trendit3User(username=username, email=email, gender=gender, thePassword=hashedPwd)
                newUserAddress = Address(country=country, state=state, local_government=local_government, trendit3_user=newUser)
                
                db.session.add_all([newUser, newUserAddress])
                db.session.commit()
            except InvalidRequestError:
                error = True
                err_msg = f"Invalid request"
                status_code = 400
                db.session.rollback()
            except IntegrityError:
                error = True
                err_msg = f"User already exists."
                status_code = 409
                db.session.rollback()
            except DataError:
                error = True
                err_msg = f"Invalid Entry"
                status_code = 400
                db.session.rollback()
            except DatabaseError:
                error = True
                err_msg = f"Error connecting to the database"
                status_code = 500
                db.session.rollback()
            except Exception as e:
                error = True
                err_msg = 'An error occurred while processing the request.'
                # Log the error details for debugging
                logging.exception("An exception occurred during registration.")
                
                status_code = 500
                db.session.rollback()
            finally:
                db.session.close()
            if error:
                return jsonify({
                        'success': False,
                        'message': err_msg,
                        'status code': status_code
                    }), status_code
            else:
                return jsonify({
                        'success': True,
                        'message': 'User registered successfully',
                        'status code': 201
                    }), 201
        else:
            abort(405)

    @staticmethod
    def login():
        error = False
        
        if request.method == 'POST':
            data = request.get_json()
            email = data.get('email')
            pwd = data.get('password')
            
            # get user from db with the email.
            user = Trendit3User.query.filter(Trendit3User.email==email).first()
            
            if user:
                if user.verify_password(pwd):
                    # User authentication successful
                    access_token = create_access_token(identity=user.id)
                    return jsonify({
                            'success': True,
                            'message': 'User logged in successfully',
                            'status code': 200,
                            'user_id': user.id,
                            'access_token': access_token,
                        }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': 'Password is incorrect',
                        'status_code': 401,
                    }), 401
            else:
                return jsonify({
                    'success': False,
                    'message': 'Email is incorrect or doesn\'t exist',
                    'status code': 401,
                }), 401
        else:
            abort(405)
