'''
This module defines the controller methods for authentication operations in the Trendit³ Flask application.

It includes methods for checking username, checking email, signing up, resending email verification code, and logging in.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

import logging
from datetime import timedelta
from flask import request, make_response
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import UnsupportedMediaType
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError, DecodeError
import pyotp

from config import Config
from ...extensions import db
from ...models import Role, RoleNames, TempUser, Trendit3User, Address, Profile, OneTimeToken, ReferralHistory, Membership, Wallet, UserSettings
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.auth_helpers import generate_six_digit_code, save_pwd_reset_token, send_2fa_code
from ...utils.helpers.user_helpers import is_user_exist, get_trendit3_user, referral_code_exists
from ...utils.helpers.mail_helpers import send_other_emails, send_code_to_email, send_url_to_email

class AuthController:
    @staticmethod
    def signUp():
        try:
            data = request.get_json()
            email = data.get('email', '').lower()
            referral_code = data.get('referral_code') # get code of referrer
            
            if not email:
                return error_response('Email is required', 400)

            if Trendit3User.query.filter_by(email=email).first():
                return error_response('Email already taken', 409)

            if referral_code and not Trendit3User.query.filter_by(username=referral_code).first():
                return error_response('Referral code is invalid', 404)
            
            # Generate a random six-digit number
            verification_code = generate_six_digit_code()
            
            try:
                send_code_to_email(email, verification_code) # send verification code to user's email
            except Exception as e:
                logging.exception(f"Error sending Email: {str(e)}")
                return error_response(f'An error occurred while sending the verification email: {str(e)}', 500)
            
            # Create a JWT that includes the user's email and the verification code
            expires = timedelta(minutes=30)
            identity = {
                'email': email,
                'verification_code': verification_code
            }
            if referral_code:
                identity['referral_code'] = referral_code
            
            signup_token = create_access_token(identity=identity, expires_delta=expires, additional_claims={'type': 'signup'})
            extra_data = {'signup_token': signup_token}
            api_response = success_response('Verification code sent successfully', 200, extra_data)
        except Exception as e:
            db.session.rollback()
            logging.exception(f"An exception occurred during registration. {e}") # Log the error details for debugging
            api_response = error_response('Error occurred processing the request.', 500)
        
        return api_response



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
            email = user_info['email']
            
            if int(entered_code) != int(user_info['verification_code']):
                return error_response('Verification code is incorrect', 400)
            
            # The entered code matches the one in the JWT, so create temporary user (TempUser)
            
            # first check if user is already a temporary user.
            user = TempUser.query.filter_by(email=email).first()
            if user:
                return success_response('User registered successfully', 201, {'user_data': user.to_dict()})
            
            new_user = TempUser(email=email)
            db.session.add(new_user)
            db.session.commit()
            
            user_data = new_user.to_dict()
            extra_data = {'user_data': user_data}
            
            # TODO: Make asynchronous
            if 'referral_code' in user_info:
                referral_code = user_info['referral_code']
                referrer = get_trendit3_user(referral_code)
                referral_history = ReferralHistory.create_referral_history(email=email, status='pending', trendit3_user=referrer, date_joined=new_user.date_joined)
            
            return success_response('User registered successfully', 201, extra_data)
        except ExpiredSignatureError as e:
            log_exception('Expired Signature Error', e)
            return error_response('The verification code has expired. Please request a new one.', 401)
        except JWTDecodeError as e:
            log_exception('JWT Decode Error', e)
            return error_response('Verification code has expired or corrupted. Please request a new one.', 401)
        except DecodeError as e:
            log_exception('JWT Decode Error', e)
            return error_response('Signup token invalid or corrupted. Make sure you are sending it correctly.', 401)
        except IntegrityError as e:
            db.session.rollback()
            logging.exception(f"Integrity Error: \n {e}")
            return error_response('User already exists.', 409)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during registration', e)
            return error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception('Exception occurred during registration', e)
            return error_response(f'An error occurred while processing the request: {str(e)}', 500)
        finally:
            db.session.close()


    @staticmethod
    def resend_email_verification_code():
        error = False
        
        try:
            data = request.get_json()
            signup_token = data.get('signup_token')
            
            # Decode the JWT and extract the user's info and the verification code
            decoded_token = decode_token(signup_token)
            user_info = decoded_token['sub']
            email = user_info['email']
            
            # Generate a random six-digit number
            new_verification_code = generate_six_digit_code()
            
            user_info.update({'verification_code': new_verification_code})
            
            try:
                send_code_to_email(email, new_verification_code) # send verification code to user's email
            except Exception as e:
                logging.exception(f"Error sending Email: {str(e)}")
                return error_response(f'Try again. An error occurred resending the verification email: {str(e)}', 500)
            
            # Create a JWT that includes the user's info and the verification code
            expires = timedelta(minutes=30)
            signup_token = create_access_token(identity=user_info, expires_delta=expires, additional_claims={'type': 'signup'})
            extra_data = {'signup_token': signup_token}
        except ExpiredSignatureError as e:
            error = True
            msg = f"The Signup token has expired. Please try signing up again."
            status_code = 401
            logging.exception(f"Expired Signature Error: {e}")
        except JWTDecodeError as e:
            error = True
            msg = f"The Signup token has expired or corrupted. Please try signing up again."
            status_code = 401
            logging.exception(f"JWT Decode Error: {e}")
        except Exception as e:
            error = True
            status_code = 500
            msg = 'An error occurred trying to resend verification code.'
            logging.exception(f"An exception occurred resending verification code. {e}") # Log the error details for debugging
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('New Verification code sent successfully', 200, extra_data)


    @staticmethod
    def complete_registration():
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            firstname = data.get('firstname', '')
            lastname = data.get('lastname', '')
            username = data.get('username', '')
            password = data.get('password', '')
            
            if not user_id:
                return error_response('User ID is required', 400)
            
            if Trendit3User.query.filter_by(username=username).first():
                return error_response('Username already taken', 409)
            
            user = TempUser.query.get(user_id)
            
            if not user:
                return error_response('User does not exist', 404)
            
            
            # Check if any field is empty
            if not all([firstname, lastname, username, password]):
                return {"error": "A required field is not provided."}, 400
            
            email = user.email
            hashed_pwd = generate_password_hash(password, "pbkdf2:sha256")
            
            new_user = Trendit3User(email=email, username=username, thePassword=hashed_pwd)
            new_user_profile = Profile(trendit3_user=new_user, firstname=firstname, lastname=lastname)
            new_user_address = Address(trendit3_user=new_user)
            new_membership = Membership(trendit3_user=new_user)
            new_user_wallet = Wallet(trendit3_user=new_user)
            new_user_setting = UserSettings(trendit3_user=new_user)
            role = Role.query.filter_by(name=RoleNames.CUSTOMER).first()
            if role:
                new_user.roles.append(role)
            
            db.session.add_all([new_user, new_user_profile, new_user_address, new_membership, new_user_wallet, new_user_setting])
            db.session.delete(user)
            db.session.commit()
            
            
            user_data = new_user.to_dict()
            
            referral = ReferralHistory.query.filter_by(email=email).first()
            if referral:
                referral.update(username=username, status='registered', date_joined=new_user.date_joined)
            
            # create access token.
            access_token = create_access_token(identity=new_user.id, expires_delta=timedelta(minutes=1440), additional_claims={'type': 'access'})
            
            extra_data = {
                'user_data': user_data,
                'access_token':access_token
            }
            
            
            # Send Welcome Email
            try:
                send_other_emails(email, email_type='welcome') # send Welcome message to user's email
            except Exception as e:
                logging.exception(f"Error sending Email: {str(e)}")
                return error_response(f'An error occurred while sending the verification email: {str(e)}', 500)
            
            return success_response('Registration completed successfully', 200, extra_data)
            
        except IntegrityError as e:
            db.session.rollback()
            log_exception('Integrity Error:', e)
            return error_response(f'User already exists: {str(e)}', 409)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during registration', e)
            return error_response('Error interacting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception('An error occurred during registration', e)
            return error_response(f'An error occurred while processing the request: {str(e)}', 500)
        finally:
            db.session.close()
    
    
    @staticmethod
    def login():
        
        try:
            data = request.get_json()
            email_username = data.get('email_username').lower()
            pwd = data.get('password')
            
            # get user from db with the email/username.
            user = get_trendit3_user(email_username)
            
            if not user:
                return error_response('Email/username is incorrect or doesn\'t exist', 401)
            
            if not user.verify_password(pwd):
                return error_response('Password is incorrect', 401)
            
            
            # Check if user has enabled 2FA
            user_settings = user.user_settings
            user_security_setting = user_settings.security_setting
            two_factor_method = user_security_setting.two_factor_method if user_security_setting else None
            
            
            identity={
                'username': user.username,
                'email': user.email,
                'two_factor_method': two_factor_method
            }
            if not user_settings or not two_factor_method:
                access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=1440), additional_claims={'type': 'access'})
                user_data = user.to_dict()
                extra_data = {'access_token':access_token, 'user_data':user_data}
                msg = 'Logged in successfully'
            elif user_security_setting and two_factor_method.lower() in ['email', 'phone']:
                # Generate 2FA code and send it to the user
                two_FA_code = generate_six_digit_code()
                
                try:
                    send_2fa_code(user, two_factor_method.lower(), two_FA_code)
                except Exception as e:
                    return error_response(f'An error occurred sending the 2FA code', 500)
                
                # Create a JWT that includes the user's info and the 2FA code
                expires = timedelta(minutes=15)
                identity.update({'two_fa_code': two_FA_code})
                two_FA_token = create_access_token(identity=identity, expires_delta=expires, additional_claims={'type': 'two_fa'})
                extra_data = { 'two_fa_token': two_FA_token }
                msg = '2 Factor Authentication code sent successfully'
            elif user_security_setting and two_factor_method.lower() == 'google_auth_app':
                expires = timedelta(minutes=30)
                two_FA_token = create_access_token(identity=identity, expires_delta=expires, additional_claims={'type': 'two_fa'})
                extra_data = { 'two_fa_token': two_FA_token }
                msg = 'Check the Google Auth App for 2 Factor Authentication code.'
            
            api_response = success_response(msg, 200, extra_data)
        
        except UnsupportedMediaType as e:
            logging.exception(f"An UnsupportedMediaType exception occurred: {e}")
            api_response = success_response(f"{str(e)}", 415)
        except Exception as e:
            logging.exception(f"An exception occurred trying to login: {e}")
            api_response = success_response(f'An Unexpected error occurred processing the request.', 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def verify_2fa():
        error = False
        try:
            data = request.get_json()
            two_FA_token = data.get('two_FA_token')
            entered_code = data.get('entered_code')
            
            try:
                # Decode the JWT and extract the user's info and the 2FA code
                decoded_token = decode_token(two_FA_token)
                token_data = decoded_token['sub']
            except ExpiredSignatureError:
                return error_response("The 2FA code has expired. Please try again.", 401)
            except Exception as e:
                return error_response(f"An unexpected error occurred: {str(e)}.", 500)
            
            if not decoded_token:
                return error_response('Invalid or expired 2FA code', 401)
            
            user = get_trendit3_user(token_data['username'])
            if not user:
                return error_response('user not found', 404)
            
            two_factor_method = token_data['two_factor_method']
            if not two_factor_method:
                return error_response('2 Factor Authentication not set', 400)
            
            elif two_factor_method.lower() in ['email', 'phone']:
                # Check if the entered code matches the one in the JWT
                if int(entered_code) != int(token_data['two_FA_code']):
                    return error_response('The wrong 2FA Code was provided. Please check your mail for the correct code and try again.', 400)
            
            elif two_factor_method.lower() == 'google_auth_app':
                secret_key = user.two_fa_secret
                
                # Verify the OTP
                totp = pyotp.TOTP(secret_key)
                if not totp.verify(entered_code):
                    return error_response('The wrong 2FA Code was provided. Please check the Google Authentication app for the correct code and try again.', 400)
            
            # 2FA token is valid, log user in.
            # User authentication successful
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=1440), additional_claims={'type': 'access'})
            user_data = user.to_dict()
            extra_data = {'access_token':access_token, 'user_data':user_data}
            
            api_response = success_response('User logged in successfully', 200, extra_data)
        except UnsupportedMediaType as e:
            logging.exception(f"An UnsupportedMediaType exception occurred: {e}")
            return error_response(f"{str(e)}", 415)
        except Exception as e:
            logging.exception(f"An exception occurred trying to login: {e}") # Log the error details for debugging
            return error_response('An error occurred while processing the request.', 500)
        
        return api_response


    @staticmethod
    def forgot_password():
        
        try:
            data = request.get_json()
            email_username = data.get('email_username').lower()
            
            # get user from db with the email/username.
            user = get_trendit3_user(email_username)
            
            if not user:
                return error_response('No account with that username or email exists.', 404)
            
            # Generate a password reset token
            expires = timedelta(minutes=15)
            reset_token = create_access_token(identity={
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }, expires_delta=expires, additional_claims={'type': 'reset-pwd', "reset": True})
            
            reset_url = f"{Config.APP_DOMAIN_NAME}/reset_password?token={reset_token}"
            
            try:
                send_url_to_email(user.email, reset_url, code_type='pwd_reset') # send reset code to user's email
            except Exception as e:
                return error_response(f'An error sending the reset URL to provided email address', 500)
            
            
            extra_data = { 'email': user.email, }
            api_response = success_response('An email with instructions to reset your password has been sent.', 200, extra_data)
            
        except Exception as e:
            log_exception(f"An exception occurred processing the request", e)
            api_response = error_response('An error occurred while processing the request.', 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def reset_password():
        
        try:
            data = request.get_json()
            reset_token = data.get('reset_token', '')
            new_password = data.get('new_password')
            hashed_pwd = generate_password_hash(new_password, "pbkdf2:sha256")
            
            try:
                # Decode the JWT and extract the user's info and the reset code
                decoded_token = decode_token(reset_token)
                if not decoded_token:
                    return error_response('Invalid or expired reset code', 401)
                
                token_data = decoded_token['sub']
            except ExpiredSignatureError:
                return error_response("This reset URL has expired. Please request a new one.", 401)
            except Exception as e:
                return error_response("An error occurred while processing the request.", 500)
            
            
            # Reset token is valid, update user password
            # get user from db with the email.
            user = get_trendit3_user(token_data['email'])
            user.update(thePassword=hashed_pwd)
            
            api_response = success_response('Password changed successfully', 200)
        except UnsupportedMediaType as e:
            db.session.rollback()
            log_exception("An UnsupportedMediaType exception occurred", e)
            api_response = error_response(f"UnsupportedMediaType: {str(e)}", 415)
        except JWTDecodeError:
            db.session.rollback()
            api_response = error_response(f"Invalid or expired reset URL", 401)
        except Exception as e:
            db.session.rollback()
            logging.exception(f"An exception occurred processing the request: {e}")
            api_response = error_response('An error occurred while processing the request.', 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def logout():
        try:
            resp = make_response(success_response('User logged out successfully', 200))
            return resp
        except Exception as e:
            resp = make_response(error_response(f'Log out failed: {e}', 500))
            return resp
    
    
    @staticmethod
    def delete_account():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            if not current_user:
                return error_response(f"user not found", 404)
            
            '''
            data = request.get_json()
            pwd = data.get('password', '')
            if not pwd:
                return error_response('Password is required', 400)
            
            if not current_user.verify_password(pwd):
                return error_response('Password is incorrect', 401)
            '''
            
            # Proceed with account deletion
            current_user.delete()
            
            api_response = success_response('account deleted successfully', 200)
            
        except Exception as e:
            db.session.rollback()
            log_exception("An exception occurred processing request", e)
            api_response = error_response('An unexpected error occurred while processing the request.', 500)
        finally:
            db.session.close()
        
        return api_response
    
    
    
    @staticmethod
    def username_check():
        try:
            data = request.get_json()
            username = data.get('username', '').lower()
            if not username:
                return error_response("username parameter is required in request's body.", 400)
            
            if is_user_exist(username, 'username'):
                return error_response(f"{username} is already Taken", 409)
            
            api_response = success_response(f"{username} is available", 200)
            
        except UnsupportedMediaType as e:
            log_exception("An exception occurred checking username", e)
            api_response = error_response("username parameter is required in request's body", 415)
        except Exception as e:
            log_exception("An exception occurred checking username", e)
            api_response = error_response("An error occurred while processing the request.", 500)
        
        return api_response
    
    
    @staticmethod
    def email_check():
        try:
            data = request.get_json()
            email = data.get('email', '').lower()
            if not email:
                return error_response("email parameter is required in request's body.", 415)
            
            if is_user_exist(email, 'email'):
                return error_response(f'{email} is already taken', 409)
            
            api_response = success_response(f"{email} is available", 200)
            
        except UnsupportedMediaType as e:
            log_exception("An exception occurred checking email", e)
            api_response = error_response("email parameter is required in request's body.", 415)
        except Exception as e:
            log_exception("An exception occurred checking email", e)
            api_response = error_response("An error occurred while processing the request.", 500)

        return api_response
    
    
    @staticmethod
    def update_user_role():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            data = request.get_json()
            
            if not data or "user_type" not in data:
                return error_response("Missing required field 'user_type'", 400)

            user_types = data["type"].strip().split(",")
            
            # Validate user types
            valid_types = ["advertiser", "earner"]
            if any(user_type not in valid_types for user_type in user_types):
                return error_response("Invalid user type", 400)
            
            # Handle empty string or extra commas
            if not user_types or any(not user_type for user_type in user_types):
                return error_response("Invalid user type format", 400)
            
            # Remove existing roles
            current_user.roles = []
            
            # Add roles based on comma-separated types
            for user_type in user_types:
                role = Role.query.filter_by(name=user_type).first()
                if role:
                    current_user.roles.append(role)
            
            db.session.commit()
            return success_response("User type updated successfully", 200)
        except Exception as e:
            db.session.rollback()
            log_exception('An error occurred assigning user roles', e)
            return error_response(f'An error occurred while processing the request: {str(e)}', 500)
        finally:
            db.session.close()
