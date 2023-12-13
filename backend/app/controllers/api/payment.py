import logging, requests, hmac, hashlib
from flask import request, jsonify, json
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import Trendit3User
from app.models.payment import Payment, Transaction
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import console_log, generate_random_string
from app.utils.helpers.payment_helpers import initialize_payment, credit_wallet
from app.utils.helpers.task_helpers import get_task_by_key
from config import Config

class PaymentController:
    @staticmethod
    def process_payment(payment_type):
        """
        Processes a payment for a user.

        This function extracts payment information from the request, checks if the user exists and if the payment has already been made. If the user exists and the payment has not been made, it initializes a transaction with Paystack. If the transaction initialization is successful, it returns a success response with the authorization URL. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the payment, a status code, and a message (and an authorization URL in case of success), and an HTTP status code.
        """
        
        data = request.get_json()
        user_id = int(get_jwt_identity())

        return initialize_payment(user_id, data, payment_type)


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
            
            # Verify transaction with Paystack
            # Extract reference from request body
            reference = data.get('reference')
            auth_headers = {
                "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
                "Content-Type": "application/json"
            }
            paystack_response = requests.get('https://api.paystack.co/transaction/verify/{}'.format(reference), headers=auth_headers)
            verification_response = paystack_response.json()
            
            
            if verification_response['status'] is False:
                return error_response(verification_response['message'], 404)
            
            # Extract needed data
            amount = verification_response['data']['amount'] / 100  # Convert from kobo to naira
            
            transaction = Transaction.query.filter_by(tx_ref=reference).first()
            if transaction:
                user_id = transaction.user_id
                payment_type = transaction.payment_type
                
                trendit3_user = Trendit3User.query.get(user_id)
                if trendit3_user is None:
                    return error_response('User does not exist', 404)
                        
                # if verification was successful
                if verification_response['status'] and verification_response['data']['status'] == 'success':
                    status_code = 200
                    msg = 'Payment verified successfully'
                    msg = f"Completed: {verification_response['data']['gateway_response']}"
                    extra_data = {}
                    
                    if transaction.status != 'Complete':
                        # Record the payment in the database
                        transaction.status = 'Complete'
                        
                        payment = Payment(trendit3_user_id=user_id, amount=amount, payment_type=payment_type, key=generate_random_string(10), payment_method='payment_gateway')
                        with db.session.begin_nested():
                            db.session.add(payment)
                    
                        # Update user's membership status in the database
                        if payment_type == 'account-activation-fee':
                            trendit3_user.activation_fee(paid=True)
                            activation_fee_paid = trendit3_user.membership.activation_fee_paid
                            
                            msg = 'Payment verified successfully and Account has been activated'
                            extra_data.update({
                                'activation_fee_paid': activation_fee_paid,
                            })
                        elif payment_type == 'membership-fee':
                            trendit3_user.membership_fee(paid=True)
                            membership_fee_paid = trendit3_user.membership.membership_fee_paid
                            
                            msg = 'Payment verified successfully and Monthly subscription fee accepted'
                            extra_data.update({
                                'membership_fee_paid': membership_fee_paid,
                            })
                        elif payment_type == 'task_creation':
                            task_key = verification_response['data']['metadata']['task_key']
                            task = get_task_by_key(task_key)
                            task.update(payment_status='Complete')
                            task_dict = task.to_dict()
                            
                            msg = 'Payment verified and Task has been created successfully'
                            extra_data.update({
                                'task': task_dict,
                            })
                        elif payment_type == 'credit-wallet':
                            # Credit user's wallet
                            try:
                                credit_wallet(user_id, amount)
                            except ValueError as e:
                                msg = f'Error crediting wallet. Please Try To Verify Again: {e}'
                                return error_response(msg, 400)
                            
                            status_code = 200
                            msg = 'Wallet Credited successfully'
                            extra_data.update({'user': trendit3_user.to_dict()})
                    
                    elif transaction.status == 'Complete':
                        if payment_type == 'account-activation-fee':
                            msg = 'Payment Completed successfully and Account is already activated'
                            extra_data.update({'activation_fee_paid': trendit3_user.membership.activation_fee_paid})
                        elif payment_type == 'membership-fee':
                            msg = 'Payment Completed successfully and Membership fee already accepted'
                            extra_data.update({'membership_fee_paid': trendit3_user.membership.membership_fee_paid,})
                        elif payment_type == 'task_creation':
                            task_key = verification_response['data']['metadata']['task_key']
                            task = get_task_by_key(task_key)
                            task_dict = task.to_dict()
                            msg = 'Payment Completed and Task has already been created successfully'
                            extra_data.update({'task': task_dict})
                        elif payment_type == 'credit-wallet':
                            msg = 'Payment Completed and Wallet already credited'
                            extra_data.update({'user': trendit3_user.to_dict()})
                    
                elif verification_response['status'] and verification_response['data']['status'] == 'abandoned':
                    # Payment was not completed
                    if transaction.status != 'Abandoned':
                        transaction.status = 'Abandoned' # update the status
                        db.session.commit()
                        
                    extra_data = {}
                    status_code = 200
                    msg = f"Abandoned: {verification_response['data']['gateway_response']}"
                else:
                    # Payment was not successful
                    if transaction.status != 'Failed':
                        transaction.status = 'Failed' # update the status
                        db.session.commit()
                        
                    error = True
                    status_code = 400
                    msg = 'Transaction verification failed: ' + verification_response['message']
            else:
                error = True
                status_code = 404
                msg = 'Transaction not found'
        except DataError as e:
            error = True
            msg = f"Invalid Entry"
            status_code = 400
            db.session.rollback()
            logging.exception("A DataError exception occurred during payment verification.", str(e))
        except DatabaseError as e:
            error = True
            msg = f"Error connecting to the database"
            status_code = 500
            db.session.rollback()
            logging.exception("A DatabaseError exception occurred during payment verification.", str(e))
        except Exception as e:
            error = True
            msg = 'An error occurred while processing the request.'
            status_code = 500
            db.session.rollback()
            logging.exception("An exception occurred during payment verification==>", str(e))
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
            signature = request.headers.get('X-Paystack-Signature') # Get the signature from the request headers
            secret_key = Config.PAYSTACK_SECRET_KEY # Get Paystack secret key
            
            data = json.loads(request.data) # Get the data from the request
            console_log('DATA', data)
            
            # Create hash using the secret key and the data
            hash = hmac.new(secret_key.encode(), msg=request.data, digestmod=hashlib.sha512)
            
            if not signature:
                return jsonify({'status': 'error', 'message': 'No signature in headers'}), 403
            
            # Verify the signature
            if not hmac.compare_digest(hash.hexdigest(), signature):
                return jsonify({'status': 'error', 'message': 'Invalid signature'}), 400
            
            # Extract needed data
            amount = data['data']['amount'] / 100  # Convert from kobo to naira
            tx_ref = f"{data['data']['reference']}"
            
            transaction = Transaction.query.filter_by(tx_ref=tx_ref).first()
            if transaction:
                user_id = transaction.user_id
                payment_type = transaction.payment_type
                trendit3_user = Trendit3User.query.with_for_update().get(user_id)

                # Check if this is a successful payment event
                if data['event'] == 'charge.success':
                    
                    if transaction.status != 'Complete':
                        # Record the payment in the database
                        transaction.status = 'Complete'
                        
                        payment = Payment(trendit3_user_id=user_id, amount=amount, payment_type=payment_type, key=generate_random_string(10), payment_method='payment_gateway')
                        with db.session.begin_nested():
                            db.session.add(payment)
                    
                        # Update user's membership status in the database
                        if payment_type == 'account-activation-fee':
                            trendit3_user.activation_fee(paid=True)
                        elif payment_type == 'membership-fee':
                            trendit3_user.membership_fee(paid=True)
                        elif payment_type == 'task_creation':
                            task_key = data['data']['metadata']['task_key']
                            task = get_task_by_key(task_key)
                            task.update(payment_status='Complete')
                        elif payment_type == 'credit-wallet':
                            # Credit user's wallet
                            try:
                                credit_wallet(user_id, amount)
                            except ValueError as e:
                                return error_response('Error crediting wallet.', 400)
                    
                    return jsonify({'status': 'success'}), 200
                elif data['event'] == 'charge.abandoned':
                    # Payment was not completed
                    if transaction.status != 'Abandoned':
                        transaction.status = 'Abandoned' # update the status
                        db.session.commit()
                        
                    return jsonify({'status': 'failed'}), 200
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

        This function extracts the current_user_id from the jwt identity, checks if the user exists, and if so, fetches the user's payment history from the database and returns it. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the request, a status code, a message (and payment history in case of success), and an HTTP status code.
        """
        error = False
        try:
            current_user_id = get_jwt_identity()
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return jsonify({
                    'status': 'failed',
                    'status_code': 404,
                    'message': 'User not found'
                }), 404
            
            # Fetch payment history from the database
            payments = Payment.query.filter_by(trendit3_user_id=current_user_id).all()
            
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
