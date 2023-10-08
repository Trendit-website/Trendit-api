import logging
import json, requests, hashlib, hmac
from flask import request, abort, jsonify
from sqlalchemy.exc import ( DataError, DatabaseError )

from app.extensions import db
from app.models.user import Trendit3User
from app.models.payment import Payment
from app.utils.helpers.payment_helpers import is_paid
from config import Config

class PaymentController:
    @staticmethod
    def process_payment():
        """
        Processes a payment for a user.

        This function extracts payment information from the request, checks if the user exists and if the payment has already been made. If the user exists and the payment has not been made, it initializes a transaction with Paystack. If the transaction initialization is successful, it returns a success response with the authorization URL. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the payment, a status code, and a message (and an authorization URL in case of success), and an HTTP status code.
        """
        error = False
        
        if request.method == 'POST':
            try:
                # Extract payment info from request
                data = request.get_json()
                user_id = int(data.get('user_id'))
                user_email = data.get('user_email')
                amount = int(data.get('amount'))
                payment_type = data.get('payment_type')
                
                Trendit3_user = Trendit3User.query.get(user_id)
                if Trendit3_user is None:
                    return jsonify({
                        'status': 'failed',
                        'status_code': 404,
                        'message': 'User not found'
                    }), 404
                
                if is_paid(user_id, payment_type):
                    return jsonify({
                        'status': 'failed',
                        'status_code': 409,
                        'message': 'Payment cannot be processed because it has already been made by the user'
                    }), 409
                
                # Convert amount to kobo (Paystack accepts amounts in kobo)
                amount_kobo = amount * 100
                
                auth_headers ={
                    "Authorization": "Bearer " + Config.PAYSTACK_SECRET_KEY,
                    "Content-Type": "application/json"
                }
                auth_data = {
                    "email": user_email,
                    "amount": amount_kobo,
                    "callback_url": "https://trendit3.vercel.app/homepage",
                    "metadata": {
                        "user_id": user_id,
                        "payment_type": payment_type
                    }
                }
                auth_data = json.dumps(auth_data)
                
                # Initialize transaction
                req = requests.post(Config.PAYSTACK_INITIALIZE_URL, headers=auth_headers, data=auth_data)
                response = json.loads(req.text)
                
                if response['status']:
                    status_code = 200
                    msg = 'Payment initialized'
                    authorization_url = response['data']['authorization_url'] # Get authorization URL from response
                else:
                    error = True
                    status_code = 400
                    msg = 'Payment initialization failed'
                    authorization_url = None
            except Exception as e:
                error = True
                msg = 'An error occurred while processing the request.'
                status_code = 500
                logging.exception("An exception occurred during registration.\n", str(e)) # Log the error details for debugging
            
            if error:
                return jsonify({
                    'status': 'failed',
                    'status_code': status_code,
                    'message': msg,
                }), status_code
            else:
                return jsonify({
                    'status': 'success',
                    'status_code': status_code,
                    'message': msg,
                    'authorization_url': authorization_url # Send success response with authorization URL
                }), status_code
        else:
            abort(405)


    @staticmethod
    def verify_payment():
        """
        Verifies a payment for a user using the Paystack API.

        This function extracts the transaction reference from the request, verifies the transaction with Paystack, and checks if the verification was successful. If the verification was successful, it updates the user's membership status in the database, records the payment in the database, and returns a success response with the payment details. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the verification, a status code, a message (and payment details in case of success), and an HTTP status code.
        """
        error = False
        try:
            # Extract user_id from request
            data = request.get_json()
            
            # Verify transaction with Paystack
            reference = data.get('reference')  # Replace with your actual transaction reference
            auth_headers = {
                "Authorization": "Bearer " + Config.PAYSTACK_SECRET_KEY,
                "Content-Type": "application/json"
            }
            req = requests.get(Config.PAYSTACK_VERIFY_URL + reference, headers=auth_headers)
            verification_response = req.json()
            
            # Check if verification was successful
            if verification_response['status'] and verification_response['data']['status'] == 'success':
                # Transaction was successful
                # Extract needed data
                amount = verification_response['data']['amount'] / 100  # Convert from kobo to naira
                user_id = verification_response['data']['metadata']['user_id']
                payment_type = verification_response['data']['metadata']['payment_type']
                
                # Update user's membership status in the database
                Trendit3_user = Trendit3User.query.get(user_id)
                if payment_type == 'activation_fee':
                    Trendit3_user.membership.activation_fee_paid = True
                elif payment_type == 'item_upload':
                    Trendit3_user.membership.item_upload_paid = True
                
                # Record the payment in the database
                payment = Payment(trendit3_user_id=user_id, amount=amount, payment_type=payment_type)
                db.session.add(payment)
                
                db.session.commit()
                
                status_code = 200
                activation_fee_paid = Trendit3_user.membership.activation_fee_paid
                item_upload_paid = Trendit3_user.membership.item_upload_paid
                
                resp = {
                    'status': 'success',
                    'message': 'Payment successfully',
                    'status_code': status_code,
                    'activation_fee_paid': activation_fee_paid,
                    'item_upload_paid': item_upload_paid,
                }
            else:
                # Transaction failed, return error message
                status_code = 400
                resp = {'status': 'failed', 'status_code': status_code, 'message': 'Transaction verification failed'}
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
            status_code = 500
            logging.exception("An exception occurred during registration.\n", str(e)) # Log the error details for debugging
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            return jsonify({
                'status': 'failed',
                'message': msg,
                'status_code': status_code
            }), status_code
        else:
            return jsonify(resp), status_code


    @staticmethod
    def handle_webhook():
        """
        Handles a webhook for a payment.

        This function verifies the signature of the webhook request, checks if the event is a successful payment event, and if so, updates the user's membership status in the database and records the payment in the database. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the webhook handling, and an HTTP status code.
        """
        try:
            # Get the signature from the request headers
            signature = request.headers.get('X-Paystack-Signature')
            
            secret_key = Config.PAYSTACK_SECRET_KEY # Get your Paystack secret key
            
            data = json.loads(request.data) # Get the data from the request
            print('\n\n-----DATA-----\n', data, '\n--------------\n\n')
            
            # Create a hash using the secret key and the data
            hash = hmac.new(secret_key.encode(), msg=request.data, digestmod=hashlib.sha512)

            # Verify the signature
            if not hmac.compare_digest(hash.hexdigest(), signature):
                abort(400)
                
            # Check if this is a successful payment event
            if data['event'] == 'charge.success':
                # Extract needed data
                amount = data['data']['amount'] / 100  # Convert from kobo to naira
                user_id = data['data']['metadata']['user_id']
                payment_type = data['data']['metadata']['payment_type']
                
                # Update user's membership status in the database
                user = Trendit3User.query.with_for_update().get(user_id)
                if payment_type == 'activation_fee':
                    user.membership.activation_fee_paid = True
                elif payment_type == 'item_upload':
                    user.membership.item_upload_paid = True
                
                # Record the payment in the database
                payment = Payment(trendit3_user_id=user_id, amount=amount, payment_type=payment_type)
                db.session.add(payment)
                db.session.commit()
                
                return jsonify({
                    'status': 'success'
                }), 200
            else:
                return jsonify({
                    'status': 'failed'
                }), 200
        except Exception as e:
            db.session.rollback()
            logging.exception("An exception occurred during registration.\n", str(e)) # Log the error details for debugging
            return jsonify({
                'status': 'failed'
            }), 500


    @staticmethod
    def get_payment_history():
        """
        Fetches the payment history for a user.

        This function extracts the user_id from the request, checks if the user exists, and if so, fetches the user's payment history from the database and returns it. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the request, a status code, a message (and payment history in case of success), and an HTTP status code.
        """
        error = False
        try:
            # Extract user_id from request
            data = request.get_json()
            user_id = int(data.get('user_id'))
            
            # Check if user exists
            user = Trendit3User.query.get(user_id)
            if user is None:
                return jsonify({
                    'status': 'failed',
                    'status_code': 404,
                    'message': 'User not found'
                }), 404
            
            # Fetch payment history from the database
            payments = Payment.query.filter_by(trendit3_user_id=user_id).all()
            
            # Convert payment history to JSON
            payment_history = [payment.to_dict() for payment in payments]
        except Exception as e:
            error = True
            status_code = 500
            msg = 'An error occurred while processing the request'
            logging.exception("An exception occurred during fetching payment history.\n", str(e)) # Log the error details for debugging
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
                'message': 'Payment history fetched successfully',
                'payment_history': payment_history
            }), 200
