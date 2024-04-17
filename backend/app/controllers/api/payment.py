import logging, requests, hmac, hashlib
from flask import request, jsonify, json
from sqlalchemy.exc import ( DataError, DatabaseError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...models import (Trendit3User, BankAccount, Recipient, Payment, Transaction, Withdrawal, TaskPaymentStatus)
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...utils.helpers.bank_helpers import get_bank_code
from ...utils.helpers.task_helpers import get_task_by_key
from ...utils.helpers.mail_helpers import send_other_emails

# import payment modules
from ...utils.payments.utils import initialize_payment, initiate_transfer
from ...utils.payments.flutterwave import verify_flutterwave_payment, flutterwave_webhook
from ...utils.payments.paystack import verify_paystack_payment, paystack_webhook
from ...utils.payments.exceptions import TransactionMissingError, CreditWalletError, SignatureError
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

        return initialize_payment(data, payment_type)


    @staticmethod
    def verify_payment():
        """
        Verifies a payment for a user using the Paystack API.

        This function extracts the transaction ID from the request, verifies the transaction with FlutterWave, and checks if the verification was successful. If the verification was successful, it updates the user's membership status in the database, records the payment in the database, and returns a success response with the payment details. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the verification, a status code, a message (and payment details in case of success), and an HTTP status code.
        """
        
        try:
            gateway = Config.PAYMENT_GATEWAY.lower()
            
            # Extract body from request
            data = request.get_json()
            
            current_user_id = get_jwt_identity()
            
            if gateway == "paystack":
                result = verify_paystack_payment(data)
            elif gateway == "flutterwave":
                result = verify_flutterwave_payment(data)
            
            msg = result['msg']
            extra_data = result['extra_data']
            
            if result['success']:
                api_response = success_response(msg, 200, extra_data)
            else:
                api_response = error_response(msg, 500, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during payment verification', e)
            return error_response('Error interacting to the database.', 500)
        except TransactionMissingError as e:
            db.session.rollback()
            return error_response(f'{e}', 500)
        except CreditWalletError as e:
            db.session.rollback()
            return error_response(f'{e}', 500)
        except Exception as e:
            db.session.rollback()
            logging.exception(f"An exception occurred during payment verification {str(e)}")
            return error_response('An error occurred while processing the request.', 500)
        finally:
            db.session.close()
        
        return api_response


    @staticmethod
    def handle_webhook():
        """
        Handles a webhook for a payment.

        This function verifies the signature of the webhook request, checks if the event is a successful payment event, and if so, updates the user's membership status in the database and records the payment in the database. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the webhook handling, and an HTTP status code.
        """
        try:
            gateway = Config.PAYMENT_GATEWAY.lower()
            
            
            if gateway == "paystack":
                result = flutterwave_webhook()
            elif gateway == "flutterwave":
                result = paystack_webhook()
            
            if result['success']:
                return jsonify({'status': 'success'}), result['status_code']
            else:
                return jsonify({'status': 'failed'}), result['status_code']
        except SignatureError as e:
            db.session.rollback()
            log_exception(f"An exception occurred Handling webhook", e)
        except ValueError as e:
            db.session.rollback()
            log_exception(f"An exception occurred", e)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception(f"error connecting to the database", e)
        except Exception as e:
            db.session.rollback()
            log_exception("An exception occurred Handling webhook", e)
            return jsonify({'status': 'failed'}), 500


    @staticmethod
    def get_payment_history():
        """
        Fetches the payment history for a user.

        This function extracts the current_user_id from the jwt identity, checks if the user exists, and if so, fetches the user's payment history from the database and returns it. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the request, a status code, a message (and payment history in case of success), and an HTTP status code.
        """
        
        try:
            current_user_id = int(get_jwt_identity())
            page = request.args.get("page", 1, type=int)
            per_page = 15
            
            # Check if user exists
            user = Trendit3User.query.get(current_user_id)
            if user is None:
                return error_response('User not found', 404)
            
            # Fetch payment records from the database
            pagination = Payment.query.filter_by(trendit3_user_id=current_user_id) \
                .order_by(Payment.created_at.desc()) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            payments = pagination.items
            current_payments = [payment.to_dict() for payment in payments]
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "payment_history": current_payments,
            }
            
            if not payments:
                return success_response(f'No payments has been made', 200, extra_data)
            
            return success_response('Payment history fetched successfully', 200, extra_data)
        except Exception as e:
            logging.exception(f"An exception occurred during fetching payment history. {str(e)}") # Log the error details for debugging
            return error_response("An error occurred while processing the request", 500)


    @staticmethod
    def withdraw():
        """
        Process for users to Withdraw money into their bank accounts.

        Returns:
            json: A JSON object containing the status of the withdrawal, a status code, and a message.
        """
        error = False
        try:
            current_user_id = int(get_jwt_identity())
            user = Trendit3User.query.get(current_user_id)
            
            data = request.get_json()
            amount = float(str(data.get('amount')).replace(',', ''))
            
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
                    return error_response("no primary bank account. Go to settings to add your primary bank account", 404)
                
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
                    
                    recipient = Recipient.create_recipient(trendit3_user=user, name=recipient_name, recipient_code=recipient_code, recipient_id=recipient_id, recipient_type=recipient_type, bank_account=bank)
            
            
            # If the withdrawal is successful, deduct the amount from the user's balance.
            initiate_transfer_response = initiate_transfer(amount, recipient, user) # with the Paystack API
            msg = f"{amount} {currency} is on it's way to {recipient.name}"
            extra_data = {
                "withdrawal_info": {
                    "amount": amount,
                    "reference": initiate_transfer_response['data']['reference'],
                    "currency": initiate_transfer_response['data']['currency'],
                    "status": initiate_transfer_response['data']['status'],
                    "created_at": initiate_transfer_response['data']['createdAt']
                }
            }
            return success_response(msg, 200, extra_data)
            
        except Exception as e:
            logging.exception(f"An exception occurred processing the withdrawal request:\n {str(e)}")
            db.session.rollback()
            return error_response(f'An error occurred while processing the withdrawal request: {str(e)}', 500)


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
                "Authorization": f"Bearer {Config.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            paystack_response = requests.get(url, headers=headers)
            verification_response = paystack_response.json()
            
            if not verification_response['status']:
                return error_response(verification_response['message'], 401)
            
            # Extract needed data
            amount = float(verification_response['data']['amount'])
            transfer_status = verification_response['data']['status']
            
            transaction = Transaction.query.filter_by(tx_ref=reference).first()
            withdrawal = Withdrawal.query.filter_by(reference=reference).first()
            
            if not transaction:
                return error_response('transaction not found', 404)
            
            if not withdrawal:
                return error_response('withdrawal not found', 404)
            
            extra_data = {'withdrawal_status': transfer_status}
            # if verification was successful
            if verification_response['status'] and transfer_status == 'success':
                msg = f"Withdrawal was successful and {amount} has been sent to provided account"
                
                if transaction.status.lower() != 'complete':
                    with db.session.begin_nested():
                        transaction.update(status='complete')  # Update transaction status
                        withdrawal.update(status=transfer_status)  # Update withdrawal status
                        user_wallet.balance -= amount  # Debit the wallet
                    
                    extra_data.update({'withdrawal_info': withdrawal.to_dict()})
                elif transaction.status.lower() == 'complete':
                    extra_data.update({'withdrawal_info': withdrawal.to_dict()})
                
                api_response = success_response(msg, 200, extra_data)
            else:
                # withdrawal was not successful
                if transaction.status.lower() != 'failed':
                    with db.session.begin_nested():
                        transaction.update(status='failed')  # Update transaction status
                        withdrawal.update(status=transfer_status)  # Update withdrawal status
                    
                    msg = f"Withdrawal was not successful please try again, or contact the admin"
                    extra_data.update({'withdrawal_info': withdrawal.to_dict()})
                
                api_response = success_response(msg, 200, extra_data)
        
        except ValueError as e:
            logging.exception(f"A ValueError occurred during withdrawal verification: {str(e)}")
            return error_response("Invalid data provided", 400)
        except requests.exceptions.RequestException as e:
            logging.exception(f"A RequestException occurred during withdrawal verification: {str(e)}")
            return error_response("Error connecting to payment gateway", 500)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            logging.exception(f"An exception occurred during database operation: {str(e)}")
            return error_response("Database error occurred", 500)
        except Exception as e:
            db.session.rollback()
            logging.exception(f"An unexpected exception occurred during withdrawal verification: {str(e)}")
            return error_response(f"An unexpected error occurred while processing the request: {str(e)}", 500)
        finally:
            db.session.close()
        
        return api_response


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


    @staticmethod
    def show_balance():
        """
        This function returns the user balance.
        
        @al-chris
        """
        try:
            current_user_id = int(get_jwt_identity())
            user = Trendit3User.query.get(current_user_id)
            user_wallet = user.wallet

            extra_data = {
                "balance": user_wallet.balance if user_wallet else None,
                'currency_name': user_wallet.currency_name if user_wallet else None,
                'currency_code': user_wallet.currency_code if user_wallet else None
            }

            return success_response(f'Balanced fetched successfully', 200, extra_data)
        
        except Exception as e:
            logging.exception(f"An exception occurred while fetching user's wallet balance: {str(e)}")
            return error_response(f"An error occurred while processing the request: {str(e)}", 500)