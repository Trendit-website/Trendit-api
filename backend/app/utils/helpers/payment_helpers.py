import requests, logging
from flask import json
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.payment import Payment, Transaction, PaystackTransaction, Withdrawal
from app.models.user import Trendit3User
from app.utils.helpers.basic_helpers import console_log, generate_random_string
from app.utils.helpers.response_helpers import error_response, success_response
from config import Config


def initialize_payment(user_id, data, payment_type=None, meta_data=None):
    """
        Initialize payment for a user.

        This function extracts payment information from the request, checks if the user exists and if the payment has already been made. If the user exists and the payment has not been made, it initializes a transaction with Paystack. If the transaction initialization is successful, it returns a success response with the authorization URL. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the payment, a status code, and a message (and an authorization URL in case of success), and an HTTP status code.
    """
    
    error = False
    
    try:
        user_id = get_jwt_identity()
        Trendit3_user = Trendit3User.query.get(user_id)
        if Trendit3_user is None:
            return error_response('User not found', 404)
        
        # get payment info
        amount = int(data.get('amount'))
        payment_type = payment_type or data.get('payment_type')
        if payment_type not in Config.PAYMENT_TYPES:
            return error_response('payment type not supported on trendit, Please reach out to the admin', 401)
        
        callback_url = data.get('callback_url')
        meta = {
            "user_id": user_id,
            "username": Trendit3_user.username,
            "payment_type": payment_type,
        }
        if meta_data:
            meta.update(meta_data)
        
        
        if is_paid(user_id, payment_type):
            return error_response('Payment cannot be processed because it has already been made by the user', 409)
        
        
        # Convert amount to kobo (Paystack accepts amounts in kobo)
        amount_kobo = amount * 100
        auth_data = {
            "email": Trendit3_user.email,
            "amount": amount_kobo,
            "callback_url": callback_url,
            "metadata": meta,
        }
        
        auth_headers ={
            "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
            "Content-Type": "application/json"
        }
        
        # Initialize the transaction
        response = requests.post(Config.PAYSTACK_INITIALIZE_URL, headers=auth_headers, data=json.dumps(auth_data))
        response_data = response.json()
        tx_ref=response_data['data']['reference'] # transaction reference
        
        if response_data['status']:
            transaction = Transaction(tx_ref=generate_random_string(15), user_id=user_id, payment_type=payment_type, status='pending')
            paystack_transaction = PaystackTransaction.create_transaction(trendit3_user=Trendit3_user, tx_ref=tx_ref, payment_type=payment_type, status='pending', amount=amount)
            db.session.add(transaction, paystack_transaction)
            db.session.commit()
            
            status_code = 200
            msg = 'Payment initialized'
            authorization_url = response_data['data']['authorization_url'] # Get authorization URL from response
            extra_data = {
                'authorization_url': authorization_url,
                'payment_type': payment_type,
                "metadata": meta
            }
        else:
            error = True
            status_code = 400
            msg = 'Payment initialization failed'
            response_data.update({"metadata": meta})
            authorization_url = None
    except Exception as e:
        error = True
        msg = 'An error occurred while processing the request.'
        status_code = 500
        response_data.update({"metadata": meta})
        logging.exception(f"An exception occurred during payment initialization:\n {str(e)}")
        db.session.rollback()
    finally:
        db.session.close()
    
    if error:
        return error_response(msg, status_code, response_data)
    else:
        return success_response(msg, status_code, extra_data)


def is_paid(user_id, payment_type):
    """
    Checks whether a user has paid a specific type of fee.

    Args:
        user_id (int): The ID of the user to check.
        payment_type (str): The type of payment to check. Can be 'membership_fee'.

    Returns:
        bool: True if the user has paid the specified fee, False otherwise.
    """
    
    paid = False
    
    Trendit3_user = Trendit3User.query.get(user_id)
    
    if payment_type == 'membership-fee':
        paid = Trendit3_user.membership.membership_fee_paid
    
    return paid


def debit_wallet(user_id, amount, payment_type=None):
    user = Trendit3User.query.get(user_id)
    console_log('USER', user)
    
    if user is None:
        raise ValueError("User not found.")
    
    wallet = user.wallet

    if wallet is None:
        raise ValueError("User does not have a wallet.")

    current_balance = wallet.balance
    if current_balance < amount:
        raise ValueError("Insufficient balance.")

    
    try:
        # Debit the wallet
        wallet.balance -= amount
        payment = Payment(trendit3_user=user, amount=amount, payment_type=payment_type, payment_method='trendit_wallet')
        
        db.session.commit()
        return 'Wallet debited successful'
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e


def credit_wallet(user_id, amount):
    user = Trendit3User.query.get(user_id)
    
    if user is None:
        raise ValueError("User not found.")
    
    wallet = user.wallet

    if wallet is None:
        raise ValueError("User does not have a wallet.")


    try:
        # Credit the wallet
        wallet.balance += amount
        db.session.commit()
        return 'wallet credited successfully'
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e


def payment_recorded(reference):
    return bool(Payment.query.filter_by(tx_ref=reference).first())



def initiate_transfer(amount, recipient, user):
    error = False
    try:
        bank_name = recipient.bank_account.bank_name
        account_no = recipient.bank_account.account_no
        reference = generate_random_string(16)
        headers = {
            "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
            "Content-Type": "application/json"
        }
        data = {
            "source": "balance",
            "amount": amount,
            "reference": reference,
            "recipient": recipient.recipient_code
        }
        request_response = requests.post(Config.PAYSTACK_TRANSFER_URL, headers=headers, json=data)
        response = request_response.json()
        reference = response['data']['reference']
        status = response['data']['status']
        
        if response['status']:
            transaction = Transaction.create_transaction(trendit3_user=user, tx_ref=reference, amount=amount, status='pending', transaction_type='withdrawal')
            withdrawal = Withdrawal.create_withdrawal(trendit3_user=user, reference=reference, amount=amount, bank_name=bank_name, account_no=account_no, status=status)
            return response
        else:
            raise Exception(f"Transfer request not initiated: {response['message']}")
    except Exception as e:
        raise e

