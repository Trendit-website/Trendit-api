import logging
from datetime import timedelta
from flask import request, jsonify, make_response
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, decode_token, set_access_cookies, unset_jwt_cookies
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError

from app.extensions import db
from app.models.user import Trendit3User, Address, Profile, OneTimeToken, ReferralHistory
from app.models.membership import Membership
from app.models.payment import Wallet
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.location_helpers import get_currency_info
from app.utils.helpers.auth_helpers import generate_six_digit_code, send_code_to_email, save_pwd_reset_token, save_2fa_token
from app.utils.helpers.user_helpers import is_email_exist, is_username_exist, get_trendit3_user, referral_code_exists

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
            referrer_code = request.args.get('referrer_code') # get code of referrer
            
            if is_email_exist(email):
                return error_response('Email already taken', 409)
                
            if is_username_exist(username):
                return error_response('Username already Taken', 409)
            
            if referrer_code and not referral_code_exists(referrer_code):
                return error_response('Referrer code is invalid', 404)
            
            hashed_pwd = generate_password_hash(password, "pbkdf2:sha256")
            
            # Generate a random six-digit number
            verification_code = generate_six_digit_code()
            
            try:
                send_code_to_email(email, verification_code) # send verification code to user's email
            except Exception as e:
                logging.exception(f"Error sending Email: {str(e)}")
                return error_response(f'An error occurred while sending the verification email: {str(e)}', 500)
            
            # Create a JWT that includes the user's info and the verification code
            expires = timedelta(minutes=30)
            identity = {
                'username': username,
                'email': email,
                'gender': gender,
                'country': country,
                'state': state,
                'local_government': local_government,
                'hashed_pwd': hashed_pwd,
                'verification_code': verification_code
            }
            if referrer_code:
                identity.update({'referrer_code': referrer_code})
            
            signup_token = create_access_token(identity=identity, expires_delta=expires, additional_claims={'type': 'signup'})
            extra_data = {'signup_token': signup_token}
        except InvalidRequestError as e:
            error = True
            msg = f"Invalid request"
            status_code = 400
            logging.exception(f"Invalid Request Error occurred: {str(e)}")
        except DataError as e:
            error = True
            msg = f"Invalid Entry"
            status_code = 400
            logging.exception(f"Data Error occurred: {str(e)}")
        except DatabaseError as e:
            error = True
            msg = f"Error connecting to the database"
            status_code = 500
            logging.exception(f"Database Error occurred: {str(e)}")
        except Exception as e:
            error = True
            status_code = 500
            msg = 'An error occurred while processing the request.'
            logging.exception(f"An exception occurred during registration. {e}") # Log the error details for debugging
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('Verification code sent successfully', 200, extra_data)


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
            hashed_pwd = user_info['hashed_pwd']
            country = user_info['country']
            state = user_info['state']
            local_government = user_info['local_government']
            
            currency_info = get_currency_info(country)
            
            if currency_info is None:
                return jsonify({
                    'status': 'failed',
                    'status_code': 500,
                    'message': 'Error getting the currency of user\'s country',
                }), 500
            
            if entered_code == user_info['verification_code']:
                # The entered code matches the one in the JWT, so create the user
                newUser = Trendit3User(username=username, email=email, gender=gender, thePassword=hashed_pwd)
                newUserAddress = Address(country=country, state=state, local_government=local_government, currency_code=currency_info['code'], trendit3_user=newUser)
                newMembership = Membership(trendit3_user=newUser)
                newUserProfile = Profile(trendit3_user=newUser)
                newUserWallet = Wallet(trendit3_user=newUser, currency_name=currency_info['name'], currency_code=currency_info['code'])
                
                db.session.add_all([newUser, newUserAddress, newUserProfile, newMembership, newUserWallet])
                db.session.commit()
                
                user_data = newUser.to_dict()
                
                if 'referrer_code' in user_info:
                    referrer_code = user_info['referrer_code']
                    profile = Profile.query.filter(Profile.referral_code == referrer_code).first()
                    referrer = profile.trendit3_user
                    referral_history = ReferralHistory.create_referral_history(username=username, status='Registered', trendit3_user=referrer, date_joined=newUser.date_joined)
            else:
                error = True
                msg = 'Verification code is incorrect'
                status_code = 400
        except ExpiredSignatureError as e:
            error = True
            msg = f"The Verification code has expired. Please request a new one."
            status_code = 401
            db.session.rollback()
            logging.exception(f"Expired Signature Error: {e}")
        except JWTDecodeError as e:
            error = True
            msg = f"Verification code has expired or corrupted. Please request a new one."
            status_code = 401
            db.session.rollback()
            logging.exception(f"JWT Decode Error: {e}")
        except InvalidRequestError as e:
            error = True
            msg = f"Invalid request"
            status_code = 400
            db.session.rollback()
            logging.exception(f"Invalid Request Error: {e}")
        except IntegrityError as e:
            error = True
            msg = f"User already exists."
            status_code = 409
            db.session.rollback()
            logging.exception(f"Integrity Error: {e}")
        except DataError as e:
            error = True
            msg = f"Invalid Entry"
            status_code = 400
            db.session.rollback()
            logging.exception(f"Data Error: {e}")
        except DatabaseError as e:
            error = True
            msg = f"Error connecting to the database"
            status_code = 500
            db.session.rollback()
            logging.exception(f"Database Error: {e}")
        except Exception as e:
            error = True
            status_code = 500
            msg = 'An error occurred while processing the request.'
            logging.exception(f"An exception occurred during registration. {e}") # Log the error details for debugging
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            extra_data = {'user_data': user_data}
            return success_response('User registered successfully', 201, extra_data)


    @staticmethod
    def login():
        error = False
        
        try:
            data = request.get_json()
            email_username = data.get('email_username')
            pwd = data.get('password')
            
            # get user from db with the email/username.
            user = get_trendit3_user(email_username)
            
            if user:
                if user.verify_password(pwd):
                    # Generate a random six-digit number
                    two_FA_code = generate_six_digit_code()
                    
                    # Create a JWT that includes the user's info and the reset code
                    expires = timedelta(minutes=15)
                    two_FA_token = create_access_token(identity={
                        'username': user.username,
                        'email': user.email,
                        'two_FA_code': two_FA_code
                    }, expires_delta=expires)
                    
                    the_two_FA_token = save_2fa_token(two_FA_token, user)
                    
                    if the_two_FA_token is None:
                        return error_response('Error saving the 2FA token to the database', 500)
                    
                    try:
                        send_code_to_email(user.email, two_FA_code, code_type='2FA') # send 2FA code to user's email
                    except Exception as e:
                        console_log('EXCEPTION', f'An error occurred while sending the 2 factor Authentication code: {str(e)}')
                        return error_response(f'An error occurred sending the 2FA code to the email address', 500)
                    
                    status_code = 200
                    msg = '2 Factor Authentication code sent successfully'
                    extra_data = { 'two_FA_token': two_FA_token }
                    
                else:
                    return error_response('Password is incorrect', 401)
            else:
                return error_response('Email/username is incorrect or doesn\'t exist', 401)
        except Exception as e:
            error = True
            status_code = 500
            msg = f'An error occurred while processing the request.'
            logging.exception(f"An exception occurred trying to login: {e}") # Log the error details for debugging
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


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
                return error_response("An error occurred while processing the request.", 500)
            
            if not decoded_token:
                return error_response('Invalid or expired 2FA code', 401)
            
            # Check if the 2FA token exists in the database
            the_two_FA_token = OneTimeToken.query.filter_by(token=two_FA_token).first()
            if not the_two_FA_token:
                console_log('DB 2FA token', the_two_FA_token)
                return error_response('The 2FA code not found. Please check your mail for the correct code and try again.', 404)
            
            if the_two_FA_token.used:
                return error_response('The 2FA Code has already been used', 403)
            
            # Check if the entered code matches the one in the JWT
            if int(entered_code) != int(token_data['two_FA_code']):
                return error_response('The wrong 2FA Code was provided. Please check your mail for the correct code and try again.', 400)
            
            # 2FA token is valid, log user in
            # User authentication successful
            # get user from db with the email/username.
            user = get_trendit3_user(token_data['email'])
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=2880), additional_claims={'type': 'access'})
            extra_data = {}
            
            # Create response
            resp = make_response(success_response('User logged in successfully', 200, extra_data))
            
            # Set access token in a secure HTTP-only cookie
            set_access_cookies(resp, access_token)
            
            # 2FA token is valid, mark it as used
            the_two_FA_token.update(used=True)
            
            return resp
        except Exception as e:
            error = True
            logging.exception(f"An exception occurred trying to login: {e}") # Log the error details for debugging
            return error_response('An error occurred while processing the request.', 500)


    @staticmethod
    def forgot_password():
        error = False
        
        try:
            data = request.get_json()
            email_username = data.get('email_username')
            
            # get user from db with the email/username.
            user = get_trendit3_user(email_username)
            
            if user:
                # Generate a random six-digit number
                reset_code = generate_six_digit_code()
                
                # Create a JWT that includes the user's info and the reset code
                expires = timedelta(minutes=15)
                reset_token = create_access_token(identity={
                    'username': user.username,
                    'email': user.email,
                    'reset_code': reset_code
                }, expires_delta=expires)
                
                pwd_reset_token = save_pwd_reset_token(reset_token, user)
                
                if pwd_reset_token is None:
                    return error_response('Error saving the reset token in the database', 500)
                
                try:
                    send_code_to_email(user.email, reset_code, code_type='pwd_reset') # send reset code to user's email
                except Exception as e:
                    console_log('EXCEPTION', f'An error occurred while sending the reset code: {str(e)}')
                    return error_response(f'An error occurred while sending the reset code to the email address', 500)
                
                status_code = 200
                msg = 'Password reset code sent successfully'
                extra_data = { 'reset_token': reset_token, 'email': user.email, }
            else:
                error = True
                status_code = 404
                msg = 'email or username isn\'t registered with us'
        except Exception as e:
            error = True
            status_code = 500
            msg = 'An error occurred while processing the request.'
            logging.exception(f"An exception occurred processing the request. {e}") # Log the error details for debugging
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def reset_password():
        error = False
        
        try:
            data = request.get_json()
            reset_token = data.get('reset_token')
            entered_code = data.get('entered_code')
            new_password = data.get('new_password')
            hashed_pwd = generate_password_hash(new_password, "pbkdf2:sha256")
            
            try:
                # Decode the JWT and extract the user's info and the reset code
                decoded_token = decode_token(reset_token)
                token_data = decoded_token['sub']
            except ExpiredSignatureError:
                return error_response("The reset code has expired. Please request a new one.", 401)
            except Exception as e:
                return error_response("An error occurred while processing the request.", 500)
            
            if not decoded_token:
                return error_response('Invalid or expired reset code', 401)
            
            # Check if the reset token exists in the database
            pwd_reset_token = OneTimeToken.query.filter_by(token=reset_token).first()
            if not pwd_reset_token:
                console_log('DB reset token', pwd_reset_token)
                return error_response('The Reset token not found.', 404)
            
            if pwd_reset_token.used:
                return error_response('The Reset Code has already been used', 403)
            
            # Check if the entered code matches the one in the JWT
            if int(entered_code) != int(token_data['reset_code']):
                return error_response('The wrong password Reset Code was provided. Please check your mail for the correct code and try again.', 400)
            
            # Reset token is valid, update user password
            # get user from db with the email.
            user = get_trendit3_user(token_data['email'])
            user.update(thePassword=hashed_pwd)
            
            # Reset token is valid, mark it as used
            pwd_reset_token.update(used=True)
            status_code = 200
            msg = 'Password changed successfully'
        except JWTDecodeError:
            error = True
            msg = f"Invalid or expired reset code"
            status_code = 401
            db.session.rollback()
        except Exception as e:
            error = True
            status_code = 500
            msg = 'An error occurred while processing the request.'
            db.session.rollback()
            logging.exception(f"An exception occurred processing the request: {e}")
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code)


    @staticmethod
    def logout():
        try:
            resp = make_response(success_response('User logged out successfully', 200))
            unset_jwt_cookies(resp)
            return resp
        except Exception as e:
            resp = make_response(error_response(f'Log out failed: {e}', 500))
            return resp
