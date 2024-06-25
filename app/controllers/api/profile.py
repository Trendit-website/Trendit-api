import logging
from datetime import timedelta
from flask import request, jsonify, current_app
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequestKeyError
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError

from ...extensions import db
from ...models import Trendit3User, Address, Profile, BankAccount, Wallet
from app.models.user import Trendit3User, Address, Profile
from ...utils.helpers.location_helpers import get_currency_info
from app.utils.helpers.basic_helpers import console_log, log_exception
from app.utils.helpers.user_helpers import get_user_info
from app.utils.helpers.media_helpers import save_media
from app.utils.helpers.user_helpers import is_username_exist, is_email_exist, save_profile_pic
from app.utils.helpers.auth_helpers import send_code_to_email, generate_six_digit_code
from ...utils.helpers.bank_helpers import get_bank_code
from app.utils.helpers.response_helpers import *

class ProfileController:
    @staticmethod
    def get_profile():
        
        try:
            current_user_id = get_jwt_identity()
            user_info = get_user_info(int(current_user_id))
            extra_data = {'user_profile': user_info}
            api_response = success_response("User profile fetched successfully", 200, extra_data)
        except Exception as e:
            log_exception("An exception occurred while getting user profile.", e)
            api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
        
        return api_response


    @staticmethod
    def edit_profile():
        try:
            current_user_id = int(get_jwt_identity())
            
            current_user = Trendit3User.query.get(current_user_id)
            
            if not current_user:
                return error_response(f"user not found", 404)
            
            user_address = current_user.address
            user_profile = current_user.profile
            user_wallet = current_user.wallet
            
            if not user_wallet:
                user_wallet = Wallet.create_wallet(trendit3_user=current_user)
            
            
            # Get the request data
            data = request.form.to_dict()
            firstname = data.get('firstname', user_profile.firstname if user_profile else '')
            lastname = data.get('lastname', user_profile.lastname if user_profile else '')
            username = data.get('username', current_user.username if current_user else '')
            gender = data.get('gender', user_profile.gender if current_user else '')
            phone = data.get('phone', user_profile.phone if current_user else '')
            country = data.get('country', user_address.country if user_address else '')
            state = data.get('state', user_address.state if user_address else '')
            local_government = data.get('local_government', user_address.local_government if user_address else '')
            birthday = data.get('birthday', user_profile.birthday if user_profile else None)
            profile_picture = request.files.get('profile_picture', '')
            
            
            currency_info = {}
            if country != user_address.country:
                currency_info = get_currency_info(country)
                
                if currency_info is None:
                    return error_response("Error getting the currency of user's country", 500)
            
            
            if is_username_exist(username, current_user):
                return error_response('Username already Taken', 409)
            
            
            save_profile_pic(current_user, profile_picture)
            
            # update user details
            current_user.update(username=username)
            user_profile.update(firstname=firstname, lastname=lastname, gender=gender, phone=phone, birthday=birthday)
            user_wallet.update(currency_name=currency_info.get('name', user_wallet.currency_name), currency_code=currency_info.get('code', user_wallet.currency_code), currency_symbol=currency_info.get('symbol', user_wallet.currency_symbol))
            user_address.update(country=country, state=state, local_government=local_government)
            
            
            extra_data={'user_data': current_user.to_dict()}
            api_response = success_response('User profile updated successfully', 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during registration', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception('An exception occurred updating user profile.', e)
            api_response = error_response('An error occurred while updating user profile', 500)
        finally:
            db.session.close()
        
        return api_response



    @staticmethod
    def update_profile():
        try:
            data = request.form.to_dict()
            current_user_id = data.get('user_id', 0)
            
            current_user = Trendit3User.query.get(current_user_id)
            
            if not current_user:
                return error_response(f"user not found", 404)
            
            user_address = current_user.address
            user_profile = current_user.profile
            user_wallet = current_user.wallet
            
            if not user_wallet:
                user_wallet = Wallet.create_wallet(trendit3_user=current_user)
            
            
            # Get the request data
            data = request.form.to_dict()
            firstname = data.get('firstname', user_profile.firstname if user_profile else '')
            lastname = data.get('lastname', user_profile.lastname if user_profile else '')
            username = data.get('username', current_user.username if current_user else '')
            gender = data.get('gender', user_profile.gender if current_user else '')
            phone = data.get('phone', user_profile.phone if current_user else '')
            country = data.get('country', user_address.country if user_address else '')
            state = data.get('country', user_address.state if user_address else '')
            local_government = data.get('local_government', user_address.local_government if user_address else '')
            birthday = data.get('birthday', user_profile.birthday if user_profile else None)
            profile_picture = request.files.get('profile_picture', '')
            
            
            currency_info = {}
            if country != user_address.country:
                currency_info = get_currency_info(country)
                
                if currency_info is None:
                    return error_response('Error getting the currency of user\'s country', 500)
            
            
            if is_username_exist(username, current_user):
                return error_response('Username already Taken', 409)
            
            
            save_profile_pic(current_user, profile_picture)
            
            # update user details
            current_user.update(username=username)
            user_profile.update(firstname=firstname, lastname=lastname, gender=gender, phone=phone, birthday=birthday)
            user_wallet.update(currency_name=currency_info.get('name', user_wallet.currency_name), currency_code=currency_info.get('code', user_wallet.currency_code), currency_symbol=currency_info.get('symbol', user_wallet.currency_symbol))
            user_address.update(country=country, state=state, local_government=local_government)
            
            
            extra_data={'user_data': current_user.to_dict()}
            api_response = success_response('User profile updated successfully', 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            api_response = error_response('Error connecting to the database.', 500)
            log_exception('Database error occurred during registration', e)
        except Exception as e:
            db.session.rollback()
            api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
            log_exception('An exception occurred updating user profile.', e)
        finally:
            db.session.close()
        
        return api_response
    

    @staticmethod
    def user_email_edit():
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
            
            extra_data = {'edit_email_token': edit_email_token}
            api_response = success_response("Verification code sent successfully", 200, extra_data)
        
        except Exception as e:
            log_exception("An exception occurred changing the email.", e)
            api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
        
        return api_response


    @staticmethod
    def verify_email_edit():
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
                extra_data = {'user_email': current_user.email}
                api_response = success_response("Email updated successfully", 201, extra_data)
            else:
                api_response = error_response("Verification code is incorrect", 400)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            api_response = error_response('Error interacting to the database.', 500)
            log_exception('Database error occurred', e)
        except Exception as e:
            db.session.rollback()
            api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
            log_exception("An exception occurred changing your email.", e)
        finally:
            db.session.close()
            
        return api_response


    @staticmethod
    def get_profile_pic():
        try:
            current_user_id = get_jwt_identity()
            user_info = get_user_info(current_user_id)
            extra_data = {
                'profile_pic': user_info.get('profile_picture', '')
            }
            api_response = success_response("profile pic fetched successfully", 200, extra_data)
        except Exception as e:
            log_exception("An exception occurred while getting user's profile pic.", e)
            api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
        
        return api_response


    @staticmethod
    def update_profile_pic():
        
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.filter(Trendit3User.id == current_user_id).first()
            
            if not current_user:
                return error_response("user not found", 404)
            
            user_profile = current_user.profile
            profile_picture = request.files.get('profile_picture', '')
            
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
            
            api_response = success_response("profile pic updated successfully", 200, extra_data)
        except BadRequestKeyError as e:
            db.session.rollback()
            log_exception("An exception occurred while updating user's profile pic.", e)
            api_response = error_response(f'{e} Make sure profile picture is sent properly', 400)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during registration', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception("An exception occurred updating user's profile pic.", 3)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        finally:
            db.session.close()
        
        return api_response

    
    @staticmethod
    def bank_details():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.filter(Trendit3User.id == current_user_id).first()
            
            if not current_user:
                return error_response("user not found", 404)
            
            primary_bank = BankAccount.query.filter_by(trendit3_user_id=current_user_id, is_primary=True).first()
            msg = "Bank details Fetched successfully" if primary_bank else "Bank details haven't been provided"
            
            if request.method == 'POST':
                # Get the request data
                data = request.get_json()
                
                bank_name = data.get('bank_name', '')
                account_no = data.get('account_no', '')
                account_name = data.get('account_name', '')
                user_country = current_user.address.country or "Nigeria"
                bank_code = get_bank_code(bank_name, user_country)
                
                if primary_bank:
                    primary_bank.update(bank_name=bank_name, bank_code=bank_code, account_no=account_no, account_name=account_name)
                else:
                    primary_bank = BankAccount.add_bank(trendit3_user=current_user, bank_name=bank_name, bank_code=bank_code, account_no=account_no, account_name=account_name, is_primary=True)
                
                msg = "Bank details updated successfully"
                extra_data = {'bank_details': primary_bank.to_dict()}
            
            extra_data = {'bank_details': primary_bank.to_dict()  if primary_bank else None}
            api_response = success_response(msg, 200, extra_data)
        except KeyError:
            if request.method == 'POST':
                db.session.rollback()
            log_exception('KeyError Exception occurred with bank details', e)
            api_response = error_response('Provide bank does not exist.', 500)
        except (DataError, DatabaseError) as e:
            if request.method == 'POST':
                db.session.rollback()
            log_exception('Database error occurred', e)
            api_response = error_response('Error interacting to the database.', 500)
        except Exception as e:
            if request.method == 'POST':
                db.session.rollback()
            log_exception('An error occurred during registration', e)
            api_response = error_response('Error creating new task. Our developers are already looking into it.', 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def membership_status():
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.filter(Trendit3User.id == current_user_id).first()
            
            if not current_user:
                return error_response("user not found", 404)
            
            membership_status = current_user.is_membership_paid
            
            extra_data = { 'membership_status': membership_status }
            
            api_response = success_response("membership status fetched", 200, extra_data)
        except Exception as e:
            log_exception("An Exception occurred checking membership status", 500)
            api_response = error_response("An unexpected error occurred. Our developers are already looking into it.", 500)
        
        return api_response
    
    