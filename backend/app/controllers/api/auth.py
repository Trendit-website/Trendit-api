import sys, random, logging
from datetime import timedelta
from flask import request, abort, jsonify, make_response
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, decode_token, set_access_cookies
from flask_jwt_extended.exceptions import JWTDecodeError

from app.extensions import db
from app.models.user import Trendit3User, Address
from app.models.membership import Membership
from app.utils.helpers.auth_helpers import is_email_exist, is_username_exist, generate_email_verification_code, send_verification_email, get_trendit3_user

class AuthController:
    @staticmethod
    def signUp():
        error = False
        
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            gender = data.get('gender')
            country = data.get('country')
            state = data.get('state')
            local_government = data.get('local_government')
            password = data.get('password')
            
            if is_email_exist(email):
                return jsonify({
                    'status': 'failed',
                    'status_code': 409,
                    'message': 'Email already Taken'
                }), 409
                
            if is_username_exist(username):
                return jsonify({
                    'status': 'failed',
                    'status_code': 409,
                    'message': 'Username already Taken'
                }), 409
            
            hashedPwd = generate_password_hash(password, "pbkdf2:sha256")
            
            # Generate a random six-digit number
            verification_code = generate_email_verification_code()
            print('\n\n',verification_code,'\n')
            
            try:
                send_verification_email(email, verification_code) # send verification code to user's email
            except Exception as e:
                return jsonify({
                    'status': 'failed',
                    'status_code': 500,
                    'message': f'An error occurred while sending the verification email: {str(e)}'
                }), 500
            
            # Create a JWT that includes the user's info and the verification code
            expires = timedelta(minutes=30)
            signup_token = create_access_token(identity={
                'username': username,
                'email': email,
                'gender': gender,
                'country': country,
                'state': state,
                'local_government': local_government,
                'hashedPwd': hashedPwd,
                'verification_code': verification_code
            }, expires_delta=expires)
            
        except InvalidRequestError:
            error = True
            msg = f"Invalid request"
            status_code = 400
        except IntegrityError:
            error = True
            msg = f"User already exists."
            status_code = 409
        except DataError:
            error = True
            msg = f"Invalid Entry"
            status_code = 400
        except DatabaseError:
            error = True
            msg = f"Error connecting to the database"
            status_code = 500
        except Exception as e:
            error = True
            msg = 'An error occurred while processing the request.'
            # Log the error details for debugging
            logging.exception("An exception occurred during registration.")
            
            status_code = 500
        
        if error:
            return jsonify({
                    'status': 'failed',
                    'status_code': status_code,
                    'message': msg
                }), status_code
        else:
            return jsonify({
                    'status': 'success',
                    'status_code': 200,
                    'message': 'Verification code sent successfully',
                    'signup_token': signup_token,
                }), 200

    @staticmethod
    def verify_email():
        error = False
        try:
            data = request.get_json()
            signup_token = data.get('signup_token')
            entered_code = data.get('entered_code')
            
            # Decode the JWT and extract the user's info and the verification code
            decoded_token = decode_token(signup_token)
            user_info = decoded_token['sub']
            username = user_info['username']
            email = user_info['email']
            gender = user_info['gender']
            hashedPwd = user_info['hashedPwd']
            country = user_info['country']
            state = user_info['state']
            local_government = user_info['local_government']
            
            if entered_code == user_info['verification_code']:
                # The entered code matches the one in the JWT, so create the user
                newUser = Trendit3User(username=username, email=email, gender=gender, thePassword=hashedPwd)
                newUserAddress = Address(country=country, state=state, local_government=local_government, trendit3_user=newUser)
                newMembership = Membership(trendit3_user=newUser)
                
                db.session.add_all([newUser, newUserAddress, newMembership])
                db.session.commit()
            else:
                error = True
                msg = 'Verification code is incorrect'
                status_code = 400
        except JWTDecodeError:
            error = True
            msg = f"Verification link has expired"
            status_code = 401
        except InvalidRequestError:
            error = True
            msg = f"Invalid request"
            status_code = 400
            db.session.rollback()
        except IntegrityError:
            error = True
            msg = f"User already exists."
            status_code = 409
            db.session.rollback()
        except DataError:
            error = True
            msg = f"Invalid Entry"
            status_code = 400
            db.session.rollback()
        except DatabaseError:
            error = True
            msg = f"Error connecting to the database"
            status_code = 500
            db.session.rollback()
        except Exception as e:
            error = True
            msg = 'An error occurred while processing the request.'
            logging.exception("An exception occurred during registration.") # Log the error details for debugging
            status_code = 500
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            return jsonify({
                    'status': 'failed',
                    'status_code': status_code,
                    'message': msg,
                }), status_code
        else:
            return jsonify({
                    'status': 'success',
                    'status_code': 201,
                    'message': 'User registered successfully',
                }), 201

    @staticmethod
    def login():
        error = False
        
        if request.method == 'POST':
            data = request.get_json()
            email_username = data.get('email_username')
            pwd = data.get('password')
            
            # get user from db with the email.
            user = get_trendit3_user(email_username)
            
            if user:
                if user.verify_password(pwd):
                    # User authentication successful
                    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=2880))
                    # Create response
                    resp = make_response(jsonify({
                        'status': 'success',
                        'message': 'User logged in successfully',
                        'status code': 200,
                        'user_id': user.id,
                    }), 200)
                    # Set access token in a secure HTTP-only cookie
                    set_access_cookies(resp, access_token)
                    return resp
                else:
                    return jsonify({
                        'status': 'failed',
                        'message': 'Password is incorrect',
                        'status_code': 401,
                    }), 401
            else:
                return jsonify({
                    'status': 'failed',
                    'message': 'Email/username is incorrect or doesn\'t exist',
                    'status code': 401,
                }), 401
        else:
            abort(405)
