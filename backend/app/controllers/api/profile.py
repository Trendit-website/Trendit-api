import logging
from datetime import timedelta
from flask import request, jsonify, current_app
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity, jwt_required
from flask_jwt_extended.exceptions import JWTDecodeError

from app.extensions import db
from app.models.user import Trendit3User, Address, Profile
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.user_helpers import get_user_info
from app.utils.helpers.media_helpers import save_media
from app.utils.helpers.user_helpers import is_username_exist, is_email_exist
from app.utils.helpers.auth_helpers import send_code_to_email, generate_six_digit_code
from app.utils.helpers.response_helpers import *

class ProfileController:
    @staticmethod
    def get_profile():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            user_info = get_user_info(current_user_id)
            extra_data = {'user_profile': user_info}
        except Exception as e:
            error = True
            msg = f'An error occurred while getting user profile: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user profile.")
            status_code = 500
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('User profile fetched successfully', 200, extra_data)


    @staticmethod
    def edit_profile():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.filter(Trendit3User.id == current_user_id).first()
            if not current_user:
                return error_response(f"user not found", 404)
            
            user_address = current_user.address
            user_profile = current_user.profile
            
            data = request.form.to_dict()
            firstname = data.get('firstname', user_profile.firstname if user_profile else '')
            lastname = data.get('lastname', user_profile.lastname if user_profile else '')
            username = data.get('username', current_user.username if current_user else '')
            gender = data.get('gender', current_user.gender if current_user else '')
            country = data.get('country', user_address.country if user_address else '')
            state = data.get('country', user_address.state if user_address else '')
            local_government = data.get('local_government', user_address.local_government if user_address else '')
            profile_picture = request.files.get('profile_picture', '')
            
            
            if is_username_exist(username, current_user):
                return error_response('Username already Taken', 409)
            
            
            if profile_picture.filename != '':
                try:
                    profile_picture_id = save_media(profile_picture) # This saves image file, saves the path in db and return the id of the image
                except Exception as e:
                    current_app.logger.error(f"An error occurred while profile image: {str(e)}")
                    return error_response(f"An error occurred saving profile image: {str(e)}", 400)
            elif profile_picture.filename == '' and current_user:
                if user_profile.profile_picture_id:
                    profile_picture_id = user_profile.profile_picture_id
                else:
                    profile_picture_id = None
            else:
                profile_picture_id = None
            
            
            # update user details
            current_user.update(gender=gender, username=username)
            user_profile.update(firstname=firstname, lastname=lastname, profile_picture_id=profile_picture_id)
            user_address.update(country=country, state=state, local_government=local_government)
            user_info = current_user.to_dict()
            extra_data={'user_profile': user_info}
        
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
            status_code = 500
            logging.exception("\n\n An exception occurred while updating user profile.")
            db.session.rollback()
        finally:
            db.session.close()
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('User profile updated successfully', 200, extra_data)


    @staticmethod
    def user_email_edit():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            data = request.get_json()
            new_email = data.get('new_email')
            
            if new_email == current_user.email:
                return error_response("email provided isn't a new email", 406)
            
            if is_email_exist(new_email, current_user):
                return error_response("Email already Taken", 409)
                
            verification_code = generate_six_digit_code() # Generate a random six-digit number
            
            try:
                send_code_to_email(new_email, verification_code) # send verification code to user's email
            except Exception as e:
                return error_response(f'An error occurred while sending the verification email: {str(e)}', 500)
            
            # Create a JWT that includes the user's info and the verification code
            expires = timedelta(minutes=30)
            edit_email_token = create_access_token(identity={
                'new_email': new_email,
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
            new_email = user_info['new_email']
            
            current_user = Trendit3User.query.get(get_jwt_identity())
            
            if int(entered_code) == int(user_info['verification_code']):
                current_user.email = new_email
                db.session.commit()
                
            else:
                error = True
                msg = 'Verification code is incorrect'
                status_code = 400
        except Exception as e:
            error = True
            msg = f'An error occurred while changing your email.'
            status_code = 500
            logging.exception("An exception occurred changing your email.")
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('Email updated successfully', 201, {'user_email': current_user.email})


    @staticmethod
    def get_profile_pic():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            user_info = get_user_info(current_user_id)
            extra_data = {
                'profile_pic': user_info.get('profile_picture', '')
            }
        except Exception as e:
            error = True
            msg = f'An error occurred while getting profile pic: {e}'
            # Log the error details for debugging
            logging.exception("An exception occurred while getting user's profile pic.")
            status_code = 500
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response("profile pic fetched successfully", 200, extra_data)


    @staticmethod
    def update_profile_pic():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.filter(Trendit3User.id == current_user_id).first()
            
            if not current_user:
                return error_response("user not found", 404)
            
            user_profile = current_user.profile
            profile_picture = request.files['profile_picture']
            
            if profile_picture.filename != '':
                try:
                    profile_picture_id = save_media(profile_picture) # This saves image file, saves the path in db and return the id of the image
                except Exception as e:
                    current_app.logger.error(f"An error occurred while saving profile image: {str(e)}")
                    return error_response(f"An error occurred saving profile image: {str(e)}", 400)
            elif profile_picture.filename == '' and current_user:
                if user_profile.profile_picture_id:
                    profile_picture_id = user_profile.profile_picture_id
                else:
                    profile_picture_id = None
            else:
                profile_picture_id = None
            
            user_profile.update(profile_picture_id=profile_picture_id)
            extra_data = {'profile_picture': user_profile.get_profile_img()}
        except Exception as e:
            error = True
            msg = f'An error occurred updating profile pic: {e}'
            status_code = 500
            logging.exception("An exception occurred while updating user's profile pic.")
            db.session.rollback()
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response("profile pic updated successfully", 200, extra_data)

