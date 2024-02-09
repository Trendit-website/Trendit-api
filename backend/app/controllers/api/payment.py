import logging, requests, hmac, hashlib
from flask import request, jsonify, json
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...models.user import Trendit3User, BankAccount, Recipient
from ...models.payment import Payment, Transaction, PaystackTransaction, Withdrawal
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, generate_random_string
from ...utils.helpers.payment_helpers import initialize_payment, credit_wallet, initiate_transfer
from ...utils.helpers.bank_helpers import get_bank_code
from ...utils.helpers.task_helpers import get_task_by_key
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
        callback_url = request.headers.get('CALLBACK-URL')
        if not callback_url:
            return error_response('callback URL not provided in the request headers', 400)
        data['callback_url'] = callback_url # add callback url to data
        
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
            
            paystack_transaction = PaystackTransaction.query.filter_by(tx_ref=reference).first()
            if paystack_transaction:
                user_id = paystack_transaction.trendit3_user_id
                payment_type = paystack_transaction.payment_type
                
                trendit3_user = Trendit3User.query.get(user_id)
                if trendit3_user is None:
                    return error_response('User does not exist', 404)
                        
                # if verification was successful
                if verification_response['status'] and verification_response['data']['status'] == 'success':
                    status_code = 200
                    msg = 'Payment verified successfully'
                    msg = f"Completed: {verification_response['data']['gateway_response']}"
                    extra_data = {}
                    
                    if paystack_transaction.status != 'complete':
                        # Record the payment in the database
                        paystack_transaction.status = 'complete'
                        
                        payment = Payment(trendit3_user=trendit3_user, amount=amount, payment_type=payment_type, payment_method=Config.PAYMENT_GATEWAY.lower())
                        with db.session.begin_nested():
                            db.session.add(payment)
                    
                        # Update user's membership status in the database
                        if payment_type == 'membership-fee':
                            trendit3_user.membership_fee(paid=True)
                            membership_fee_paid = trendit3_user.membership.membership_fee_paid
                            
                            msg = 'Payment verified successfully and Account has been activated'
                            extra_data.update({
                                'membership_fee_paid': membership_fee_paid,
                            })
                        elif payment_type == 'task-creation':
                            task_key = verification_response['data']['metadata']['task_key']
                            task = get_task_by_key(task_key)
                            task.update(payment_status='complete')
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
                    
                    elif paystack_transaction.status == 'complete':
                        if payment_type == 'membership-fee':
                            msg = 'Payment Completed successfully and Account is already activated'
                            extra_data.update({'membership_fee_paid': trendit3_user.membership.membership_fee_paid,})
                        elif payment_type == 'task-creation':
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
                    if paystack_transaction.status != 'abandoned':
                        paystack_transaction.update(status='abandoned') # update the status
                        db.session.commit()
                        
                    extra_data = {}
                    status_code = 200
                    msg = f"Abandoned: {verification_response['data']['gateway_response']}"
                
                else:
                    # Payment was not successful
                    if paystack_transaction.status != 'Failed':
                        paystack_transaction.update(status='failed') # update the status
                        
                    error = True
                    status_code = 400
                    msg = 'Payment verification failed: ' + verification_response['message']
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
            
            paystack_transaction = PaystackTransaction.query.filter_by(tx_ref=tx_ref).first()
            if paystack_transaction:
                user_id = paystack_transaction.user_id
                payment_type = paystack_transaction.payment_type
                trendit3_user = Trendit3User.query.with_for_update().get(user_id)

                # Check if this is a successful payment event
                if data['event'] == 'charge.success':
                    
                    if paystack_transaction.status != 'complete':
                        # Record the payment in the database
                        paystack_transaction.status = 'complete'
                        
                        payment = Payment(trendit3_user=trendit3_user, amount=amount, payment_type=payment_type, payment_method=Config.PAYMENT_GATEWAY.lower())
                        with db.session.begin_nested():
                            db.session.add(payment)
                    
                        # Update user's membership status in the database
                        if payment_type == 'membership-fee':
                            trendit3_user.membership_fee(paid=True)
                        elif payment_type == 'task-creation':
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
                    if paystack_transaction.status != 'Abandoned':
                        paystack_transaction.status = 'Abandoned' # update the status
                        db.session.commit()
                        
                    return jsonify({'status': 'failed'}), 200
                else:
                    # Payment was not successful
                    if paystack_transaction.status != 'Failed':
                        paystack_transaction.status = 'Failed' # update the status
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


    @staticmethod
    def withdraw():
        """
        Process for users to Withdraw money into their bank accounts.

        Returns:
            json: A JSON object containing the status of the withdrawal, a status code, and a message.
        """
        error = False
        try:
            current_user_id = get_jwt_identity()
            user = Trendit3User.query.get(current_user_id)
            
            data = request.get_json()
            amount = data.get('amount')
            
            if user.wallet_balance < amount:
                return error_response("Insufficient balance", 400)
            
            name = user.profile.firstname
            is_primary = data.get('is_primary', True)
            bank_name = data.get('bank_name')
            account_no = data.get('account_no')
            bank_code = get_bank_code(bank_name)
            currency = user.wallet.currency_code
            
            if is_primary:
                primary_bank = BankAccount.query.filter_by(trendit3_user_id=user.id, is_primary=True).first()
                if not primary_bank:
                    return error_response("no primary bank account. Edit you profile to add a primary bank account", 404)
                
                recipient = primary_bank.recipient
                
            else:
                bank = BankAccount.add_bank(trendit3_user=user, bank_name=bank_name, bank_code=bank_code, account_no=account_no, is_primary=False)
                recipient = bank.recipient
                if not recipient:
                    
                    headers = {
                        "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
                        "Content-Type": "application/json"
                    }
                    data = {
                        "type": "nuban",
                        "name": name,
                        "account_number": str(account_no),
                        "bank_code": str(bank_code),
                    }
                    request_response = requests.post(Config.PAYSTACK_RECIPIENT_URL, headers=headers, data=json.dumps(data))
                    response = request_response.json()
                    recipient_name = response['data']['details']['account_name']
                    recipient_code = response['data']['recipient_code']
                    recipient_type = response['data']['type']
                    recipient_id = response['data']['id']
                    
                    
                    if response['status'] is False:
                        return error_response(response['message'], 401)
                    
                    recipient = Recipient.create_recipient(trendit3_user=user, name=recipient_name, recipient_code=recipient_code, recipient_id=recipient_id, recipient_type=recipient_type, bank_account=primary_bank)
            
            
            # If the withdrawal is successful, deduct the amount from the user's balance.
            initiate_transfer_response = initiate_transfer(amount, recipient, user) # with the Paystack API
            msg = f"{amount} {currency} is on it's way to {recipient.name}"
            status_code = 200
            extra_data = {
                "withdrawal_info": {
                    "amount": amount,
                    "reference": initiate_transfer_response['data']['reference'],
                    "currency": initiate_transfer_response['data']['currency'],
                    "status": initiate_transfer_response['data']['status'],
                    "created_at": initiate_transfer_response['data']['createdAt'],
                    "updated_at": initiate_transfer_response['data']['updatedAt']
                }
            }
            
        except Exception as e:
            error = True
            status_code = 500
            msg = f'An error occurred while processing the withdrawal request: {str(e)}'
            logging.exception(f"An exception occurred processing the withdrawal request:\n {str(e)}")
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, 200, extra_data)


    @staticmethod
    def verify_withdraw():
        error = False
        try:
            current_user_id = get_jwt_identity()
            user = Trendit3User.query.get(current_user_id)
            user_wallet = user.wallet
            
            data = request.get_json()
            reference = data.get('reference', '')
            if not reference:
                return error_response("reference key is required in request's body", 401)
            
            url = f"https://api.paystack.co/transfer/verify/{reference}"
            headers = {
                "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
                "Content-Type": "application/json"
            }
            paystack_response = requests.get(url, headers=headers)
            verification_response = paystack_response.json()
            if verification_response['status'] is False:
                return error_response(verification_response['message'], 401)
            
            # Extract needed data
            amount = verification_response['data']['amount']
            transfer_status = verification_response['data']['status']
            
            transaction = Transaction.query.filter_by(tx_ref=reference).first()
            withdrawal = Withdrawal.query.filter_by(reference=reference).first()
            
            if not transaction:
                return error_response('transaction not found', 404)
            
            if not withdrawal:
                return error_response('withdrawal not found', 404)
            
            # if verification was successful
            if verification_response['status'] and transfer_status == 'success':
                status_code = 200
                msg = f"Withdrawal was successful and {amount} has been sent to provided account"
                extra_data = {}
                
                if transaction.status != 'complete':
                    transaction.status = 'complete' # Record the transaction in the database
                    withdrawal.status = transfer_status
                    user_wallet.balance -= amount # Debit the wallet
                    
                    extra_data.update({
                        'withdrawal_info': withdrawal.to_dict(),
                    })
                elif transaction.status == 'complete':
                    extra_data.update({
                        'withdrawal_info': withdrawal.to_dict(),
                    })
            else:
                # withdrawal was not successful
                if transaction.status != 'failed':
                    transaction.status = 'failed' # update the status
                    withdrawal.status = transfer_status
                
                error = True
                status_code = 400
                msg = f"Withdrawal was not successful please try again, or contact the admin"
                extra_data = {}
                
        except DataError as e:
            error = True
            msg = f"Invalid Entry: {str(e)}"
            status_code = 400
            db.session.rollback()
            logging.exception(f"A DataError exception occurred during withdrawal verification ==> \n {str(e)}")
        except DatabaseError as e:
            error = True
            msg = f"Error connecting to the database: {str(e)} "
            status_code = 500
            db.session.rollback()
            logging.exception(f"A DatabaseError exception occurred during withdrawal verification ==> \n {str(e)}")
        except Exception as e:
            error = True
            msg = f"An error occurred while processing the request: {str(e)}"
            status_code = 500
            db.session.rollback()
            logging.exception(f"An exception occurred during withdrawal verification ==> \n {str(e)}")
        finally:
            db.session.close()
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    
    @staticmethod
    def withdraw_approval_webhook():
        error = False
        try:
            data = request.get_json()
            recipient_code = data.get('recipient_code')
            amount = data.get('amount')

            # Check if recipient code exists in db records
            recipient = Recipient.query.filter_by(recipient_code=recipient_code).first()
            if recipient:
                return jsonify(message='Transfer approved'), 200 # Respond with a 200 OK if details are authentic
            else:
                # Respond with a 400 Bad Request if details are invalid
                return jsonify(error='Invalid transfer details'), 400
        except Exception as e:
            print(f"Error handling approval: {e}")
            return jsonify(error='Internal Server Error'), 500
    