import logging
import json, requests, hashlib, hmac
from flask import request, abort, jsonify
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import Trendit3User
from app.models.payment import Payment, Transaction
from app.models.task import Task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.utils.helpers.payment_helpers import is_paid, initialize_payment
from app.utils.helpers.task_helpers import get_task_by_ref
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
        
        data = request.get_json()
        user_id = int(get_jwt_identity())

        return initialize_payment(user_id, data)


    @staticmethod
    def verify_payment():
        """
        Verifies a payment for a user using the Paystack API.

        This function extracts the transaction ID from the request, verifies the transaction with FlutterWave, and checks if the verification was successful. If the verification was successful, it updates the user's membership status in the database, records the payment in the database, and returns a success response with the payment details. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the verification, a status code, a message (and payment details in case of success), and an HTTP status code.
        """
        error = False
        try:
            # Extract body from request
            data = request.get_json()
            
            # Verify transaction with FlutterWave
            # Extract transaction_id from request body
            transaction_id = data.get('transaction_id')
            headers = {
                "Authorization": "Bearer {}".format(Config.FLUTTER_SECRET_KEY),
                "Content-Type": "application/json"
            }
            flutter_response = requests.get(f'https://api.flutterwave.com/v3/transactions/{transaction_id}/verify', headers=headers)
            response_data = flutter_response.json()
            
            # Extract needed data
            amount = response_data['data']['amount']
            tx_ref = response_data['data']['tx_ref']
            
            transaction = Transaction.query.filter_by(tx_ref=tx_ref).first()
            if transaction:
                user_id = transaction.user_id
                payment_type = transaction.payment_type
                
                Trendit3_user = Trendit3User.query.get(user_id)
                if Trendit3_user is None:
                    return error_response('User does not exist', 404)
                        
                # if verification was successful
                if response_data['status'] == 'success':
                    status_code = 200
                    msg = 'Payment verified successfully'
                    extra_data = {}
                    if transaction.status != 'Complete':
                        # Record the payment in the database
                        transaction.status = 'Complete'
                        payment = Payment(trendit3_user_id=user_id, amount=amount, payment_type=payment_type)
                        db.session.add(payment)
                        db.session.commit()
                    
                    # Update user's membership status in the database
                    if payment_type == 'activation_fee':
                        Trendit3_user.activation_fee(paid=True)
                        activation_fee_paid = Trendit3_user.membership.activation_fee_paid
                        
                        msg = 'Payment verified successfully and Account has been activated'
                        extra_data.update({
                            'activation_fee_paid': activation_fee_paid,
                        })
                    elif payment_type == 'item_upload':
                        Trendit3_user.marketplace_upload_fee(paid=True)
                        item_upload_paid = Trendit3_user.membership.item_upload_paid
                        
                        msg = 'Payment verified successfully and Monthly subscription fee accepted'
                        extra_data.update({
                            'item_upload_paid': item_upload_paid,
                        })
                    elif payment_type == 'task_creation':
                        task_ref = response_data['data']['meta']['task_ref']
                        task = get_task_by_ref(task_ref)
                        task.update(payment_status='Complete')
                        task_dict = task.to_dict()
                        
                        msg = 'Payment verified and Task has been created successfully'
                        extra_data.update({
                            'task': task_dict,
                        })
                    
                else:
                    # Payment was not successful
                    if transaction.status != 'Failed':
                        transaction.status = 'Failed' # update the status
                        db.session.commit()
                        
                    error = True
                    status_code = 400
                    msg = 'Transaction verification failed: ' + response_data['message']
            else:
                error = True
                status_code = 404
                msg = 'Transaction not found'
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
            logging.exception("An exception occurred during registration.\n", str(e))
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def handle_webhook():
        """
        Handles a webhook for a payment.

        This function verifies the signature of the webhook request, checks if the event is a successful payment event, and if so, updates the user's membership status in the database and records the payment in the database. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the webhook handling, and an HTTP status code.
        """
        try:
            signature = request.headers.get('verif-hash') # Get the signature from the request headers
            
            if not signature:
                return jsonify({'status': 'error', 'message': 'No signature in headers'}), 403
            
            # Check if the signature is correct
            if signature != Config.FLUTTER_SECRET_HASH:
                return jsonify({'status': 'error', 'message': 'Invalid signature'}), 400
            
            payload = request.get_json() # Get the payload from the request
            data = payload['data']
            
            tx_ref = data['tx_ref']
            transaction = Transaction.query.filter_by(tx_ref=tx_ref).first()
            if transaction:
                user_id = transaction.user_id
                payment_type = transaction.payment_type
            
                # Check if this is a successful payment event
                if data['status'] == 'successful':
                    # Extract needed data
                    amount = data['amount']
                    
                    if transaction.status != 'Complete':
                        # Update user's membership status in the database
                        user = Trendit3User.query.with_for_update().get(user_id)
                        if payment_type == 'activation_fee':
                            user.membership.activation_fee_paid = True
                        elif payment_type == 'item_upload':
                            user.membership.item_upload_paid = True
                        
                        # Record the payment in the database
                        transaction.status = 'Complete'
                        payment = Payment(trendit3_user_id=user_id, amount=amount, payment_type=payment_type)
                        db.session.add(payment)
                        db.session.commit()
                    
                    return jsonify({'status': 'success'}), 200
                else:
                    # Payment was not successful
                    if transaction.status != 'Failed':
                        transaction.status = 'Failed' # update the status
                        db.session.commit()
                    return jsonify({'status': 'failed'}), 200
            else:
                return jsonify({'status': 'failed'}), 404
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
