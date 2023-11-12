import sys, random, logging
from datetime import timedelta
from flask import request, abort, jsonify, make_response, current_app
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from flask_jwt_extended import create_access_token, decode_token, set_access_cookies, get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTDecodeError

from app.extensions import db
from app.models.user import Trendit3User, Address, Profile
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.location_helpers import get_currency_info
from app.utils.helpers.user_helpers import get_user_info
from app.utils.helpers.img_helpers import save_image
from app.utils.helpers.user_helpers import is_username_exist, is_email_exist
from app.utils.helpers.auth_helpers import send_code_to_email, generate_email_verification_code

class ProfileController:
    @staticmethod
    def get_profile():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            user_info = get_user_info(current_user_id)
            pass
        except Exception as e:
            error = True
            msg = f'An error occurred while getting user profile: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user profile.")
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
                    'message': 'User profile fetched successfully',
                    'user_data': user_info
                }), 200
        
        
    @staticmethod
    def edit_profile():
        error = False
        
        try:
            data = request.form.to_dict()
            firstname = data.get('firstname', '')
            lastname = data.get('lastname', '')
            username = data.get('username', '')
            gender = data.get('gender', '')
            country = data.get('country', '')
            state = data.get('state', '')
            local_government = data.get('local_government', '')
            profile_picture = request.files['profile_picture']
            
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.filter(Trendit3User.id == current_user_id).first()
            user_address = current_user.address
            user_profile = current_user.profile
            
            if is_username_exist(username, current_user):
                return jsonify({
                    'status': 'failed',
                    'status_code': 409,
                    'message': 'Username already Taken'
                }), 409
            
            
            if profile_picture.filename != '':
                try:
                    profile_picture_id = save_image(profile_picture) # This saves image file, saves the path in db and return the id of the image
                except Exception as e:
                    current_app.logger.error(f"An error occurred while saving image for item {data.get('name')}: {str(e)}")
                    return None
            elif profile_picture.filename == '' and current_user:
                if user_profile.profile_picture_id:
                    profile_picture_id = user_profile.profile_picture_id
                else:
                    profile_picture_id = None
            else:
                profile_picture_id = None
            
            
            # update user details
            if current_user:
                current_user.update(gender=gender, username=username)
                user_profile.update(firstname=firstname, lastname=lastname, profile_picture_id=profile_picture_id   )
                user_address.update(country=country, state=state, local_government=local_government)
                user_data = current_user.to_dict()
            else:
                error = True
                msg = f"user not found"
                status_code = 404
        except InvalidRequestError:
            error = True
            msg = f"Invalid request"
            status_code = 400
            db.session.rollback()
        except DataError:
            error = True
            msg = f"Invalid Entry"
            db.session.rollback()
            status_code = 400
        except DatabaseError:
            error = True
            msg = f"Error connecting to the database"
            status_code = 500
            db.session.rollback()
        except Exception as e:
            error = True
            msg = f'An error occurred while updating user profile: {e}'
            # Log the error details for debugging
            logging.exception("\n\n An exception occurred while updating user profile.")
            status_code = 500
            db.session.rollback()
        finally:
            db.session.close()
        
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
                    'message': 'User profile updated successfully',
                    'user_data': user_data
                }), 200


    @staticmethod
    @jwt_required()
    def user_email_edit():
        error = False
        
        try:
            data = request.get_json()
            email = data.get('email')
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            
            if email == current_user.email:
                return jsonify({
                    'status': 'failed',
                    'status_code': 400,
                    'message': 'email provided isn\'t a new email'
                })
            
            if is_email_exist(email, current_user):
                return jsonify({
                    'status': 'failed',
                    'status_code': 409,
                    'message': 'Email already Taken'
                }), 409
                
            verification_code = generate_email_verification_code() # Generate a random six-digit number
            console_log('VERIFICATION CODE', verification_code)
            
            try:
                send_code_to_email(email, verification_code) # send verification code to user's email
            except Exception as e:
                return jsonify({
                    'status': 'failed',
                    'status_code': 500,
                    'message': f'An error occurred while sending the verification email: {str(e)}'
                }), 500
            
            # Create a JWT that includes the user's info and the verification code
            expires = timedelta(minutes=30)
            edit_email_token = create_access_token(identity={
                'email': email,
                'user_id': get_jwt_identity(),
                'verification_code': verification_code
            }, expires_delta=expires)
        except Exception as e:
            error = True
            msg = f'An error occurred trying to change the email: {e}'
            status_code = 500
            # Log the error details for debugging
            logging.exception("An exception occurred changing the email.")
        
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
                    'edit_email_token': edit_email_token,
                }), 200


    @staticmethod
    def verify_email_edit():
        error = False
        try:
            data = request.get_json()
            edit_email_token = data.get('edit_email_token')
            entered_code = data.get('entered_code')
            
            # Decode the JWT and extract the user's info and the verification code
            decoded_token = decode_token(edit_email_token)
            user_info = decoded_token['sub']
            new_email = user_info['email']
            
            current_user = Trendit3User.query.get(get_jwt_identity())
            
            if int(entered_code) == int(user_info['verification_code']):
                current_user.email = new_email
                db.session.commit()
                
                user_data = current_user.to_dict()
            else:
                error = True
                msg = 'Verification code is incorrect'
                status_code = 400
        except Exception as e:
            error = True
            msg = f'An error occurred while changing your email.'
            status_code = 500
            # Log the error details for debugging
            logging.exception("An exception occurred changing your email.")
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
                    'status_code': 200,
                    'message': 'Email changed successfully',
                    'user_data': user_data
                }), 201
