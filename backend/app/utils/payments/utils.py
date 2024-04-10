'''
This module defines helper functions for handling payments in the Trendit³ Flask application.

These functions assist with tasks such:
    * checking payment.
    * payment initialization
    * transaction processing
    * payment verification
    * crediting and debiting user wallet

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from datetime import datetime
import requests, logging
from flask import json
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, sql
from sqlalchemy.exc import ( DataError, DatabaseError )

from ...extensions import db
from ...models import Payment, Transaction, TransactionType, Withdrawal, Trendit3User
from ...utils.helpers.basic_helpers import console_log, log_exception, generate_random_string
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.mail_helpers import send_other_emails
from config import Config

def construct_payload(amount: int, callback_url: str, meta: dict, user: Trendit3User):
    gateway = Config.PAYMENT_GATEWAY.lower()
    payload = {}
    
    # Construct the payload for Flutterwave API
    if gateway == "paystack":
        # Convert amount to kobo (Paystack accepts amounts in kobo)
        amount_kobo = amount * 100
        payload = {
            "email": user.email,
            "amount": amount_kobo,
            "callback_url": callback_url,
            "metadata": meta,
        }
    elif gateway == "flutterwave":
        payload = {
            "tx_ref": f"{generate_random_string(4)}-{generate_random_string(8)}",
            "amount": amount,
            "currency": "NGN",
            "redirect_url": callback_url,
            "meta": meta,
            "customer": {
                "email": user.email,
                "name": user.full_name
            },
            "customizations": {
                "title": "Pied Piper Payments",
                "logo": "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.png"
            }
        }
    
    return payload

def initialize_flutterwave_payment(amount: int, payload: dict, payment_type: str, user: Trendit3User):
    try:
        auth_headers ={
            "Authorization": "Bearer {}".format(Config.FLW_SECRET_KEY),
            "Content-Type": "application/json"
        }
        
        response = requests.post(Config.FLW_INITIALIZE_URL, headers=auth_headers, json=payload)
        status_code = int(response.status_code)
        console_log('response', response)
        
        response_data = response.json()
        console_log('response_data', response_data)
        console_log('ref', payload['tx_ref'])
        
        if 'status' in response_data:
            if response_data['status'] == 'success':
                tx_ref=payload['tx_ref'] # transaction reference
                transaction = Transaction(key=tx_ref, amount=amount, transaction_type=TransactionType.PAYMENT, description=f'{payment_type}payment', status='pending', trendit3_user=user)
                payment = Payment(key=tx_ref, amount=amount, payment_type=payment_type, payment_method=Config.PAYMENT_GATEWAY.lower(),status='pending', trendit3_user=user)
                db.session.add_all([transaction, payment])
                db.session.commit()
                
                authorization_url = response_data['data']['link'] # Get authorization URL from response
                status = True
                extra_data = {
                    'authorization_url': authorization_url,
                    'payment_type': payment_type,
                    "metadata": payload['meta'],
                    "status_code": status_code
                }
            else:
                status = False
                response_data.update({"metadata": payload['meta'], "status_code": status_code})
                extra_data = response_data
        else:
            status = False
            response_data.update({"status_code": status_code})
            extra_data = response_data
    except (DataError, DatabaseError) as e:
        db.session.rollback()
        status = False
        raise e
    except Exception as e:
        status = False
        raise e
    
    return status, extra_data

def initialize_paystack_payment(amount: int, payload: dict, payment_type: str, user: Trendit3User) -> tuple[bool, dict]:
    try:
        auth_headers ={
            "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
            "Content-Type": "application/json"
        }
        
        response = requests.post(Config.PAYSTACK_INITIALIZE_URL, headers=auth_headers, data=json.dumps(payload))
        status_code = int(response.status_code)
        console_log('response', response)
        
        response_data = response.json()
        console_log('response_data', response_data)
        
        if 'status' in response_data:
            if response_data['status']:
                tx_ref=response_data['data']['reference'] # transaction reference
                transaction = Transaction(key=tx_ref, amount=amount, transaction_type=TransactionType.PAYMENT, description=f'{payment_type}payment', status='pending', trendit3_user=user)
                payment = Payment(key=tx_ref, amount=amount, payment_type=payment_type, payment_method=Config.PAYMENT_GATEWAY.lower(),status='pending', trendit3_user=user)
                db.session.add_all([transaction, payment])
                db.session.commit()
                
                authorization_url = response_data['data']['authorization_url'] # Get authorization URL from response
                status = True
                extra_data = {
                    'authorization_url': authorization_url,
                    'payment_type': payment_type,
                    "metadata": payload['metadata'],
                    "status_code": status_code
                }
            else:
                status = False
                response_data.update({"metadata": payload['metadata'], "status_code": status_code})
                extra_data = response_data
        else:
            status = False
            response_data.update({"status_code": status_code})
            extra_data = response_data
    except (DataError, DatabaseError) as e:
        db.session.rollback()
        status = False
        raise e
    except Exception as e:
        status = False
        raise e
    
    return status, extra_data

def initialize_payment(user_id, data, payment_type=None, meta_data=None):
    """
        Initialize payment for a user.

        This function extracts payment information from the request, checks if the user exists and if the payment has already been made. If the user exists and the payment has not been made, it initializes a transaction with Paystack. If the transaction initialization is successful, it returns a success response with the authorization URL. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            json, int: A JSON object containing the status of the payment, a status code, and a message (and an authorization URL in case of success), and an HTTP status code.
    """
    
    gateway = Config.PAYMENT_GATEWAY.lower()
    meta = {}
    
    try:
        current_user_id = get_jwt_identity()
        current_user = Trendit3User.query.get(current_user_id)
        if current_user is None:
            return error_response('User not found', 404)
        
        # get payment info
        amount = float(str(data.get('amount')).replace(',', ''))
        payment_type = payment_type or data.get('payment_type')
        if payment_type not in Config.PAYMENT_TYPES:
            return error_response('payment type not supported on trendit, Please reach out to the admin', 406)
        
        callback_url = data.get('callback_url')
        meta = {
            "user_id": user_id,
            "email": current_user.email,
            "username": current_user.username,
            "payment_type": payment_type,
        }
        if meta_data:
            meta.update(meta_data)
        
        
        if is_paid(user_id, payment_type):
            return error_response('Payment cannot be processed because it has already been made.', 409)
        
        payload = construct_payload(amount=amount, callback_url=callback_url, meta=meta, user=current_user)
        
        
        # Initialize the payment
        if gateway == "paystack":
            status, extra_data = initialize_paystack_payment(amount=amount, payload=payload, payment_type=payment_type, user=current_user)
        elif gateway == "flutterwave":
            status, extra_data = initialize_flutterwave_payment(amount=amount, payload=payload, payment_type=payment_type, user=current_user)
        
        if status:
            api_response = success_response('Payment initialized', extra_data['status_code'], extra_data)
        else:
            api_response = error_response('Payment initialization failed', extra_data['status_code'], extra_data)
    except (DataError, DatabaseError) as e:
        db.session.rollback()
        log_exception(f"Error connecting to the database", e)
        api_response = error_response('Error connecting to the database', 500)
    except Exception as e:
        db.session.rollback()
        log_exception(f"An exception occurred during payment initialization", e)
        api_response = error_response('An error occurred initializing payment.', 500)
    finally:
        db.session.close()
    
    return api_response


def is_paid(user_id: int, payment_type: str) -> bool:
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


def debit_wallet(user_id: int, amount: int, payment_type=None) -> float:
    user = Trendit3User.query.get(user_id)
    
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
        key = generate_random_string(16)
        payment = Payment(key=key, amount=amount, payment_type=payment_type, payment_method='wallet', status='complete', trendit3_user=user)
        transaction = Transaction(key=key, amount=amount, transaction_type=TransactionType.DEBIT, status='complete', trendit3_user=user)
        
        db.session.add(payment, transaction)
        db.session.commit()
        send_other_emails(user.email, email_type='debit', amount=amount) # send debit alert to user's mail
        return wallet.balance
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e


def credit_wallet(user_id: int, amount: int) -> float:
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
        return wallet.balance
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
            transaction = Transaction.create_transaction(key=reference, amount=amount, transaction_type=TransactionType.WITHDRAWAL, status='pending', trendit3_user=user)
            withdrawal = Withdrawal.create_withdrawal(reference=reference, amount=amount, bank_name=bank_name, account_no=account_no, status=status, trendit3_user=user)
            return response
        else:
            raise Exception(f"Transfer request not initiated: {response['message']}")
    except Exception as e:
        raise e



# Transaction Helpers
def get_total_amount_spent(user_id):
    """
    Get the total amount spent by the user, both overall and in the current month.

    Args:
        user_id (int): The ID of the user.

    Returns:
        tuple: A tuple containing the total amount spent overall and the total amount spent in the current month.
    """
    
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calculate total amount spent by the current user in the current month
    total_spent_current_month = db.session.query(
        func.sum(Payment.amount)
    ).filter(
        Payment.trendit3_user_id == user_id,
        Payment.payment_type != 'credit-wallet',
        db.extract('month', Payment.created_at) == current_month,
        db.extract('year', Payment.created_at) == current_year
    ).scalar() or 0.0
    
    # Calculate total amount spent by the current user across all payments ever made
    total_spent_overall = db.session.query(
        func.sum(Payment.amount)
    ).filter(
        Payment.trendit3_user_id == user_id,
        Payment.payment_type != 'credit-wallet'
    ).scalar() or 0.0
    
    
    return total_spent_overall, total_spent_current_month


def get_total_amount_earned(user_id):
    """
    Get the total amount earned by the user, both overall and in the current month.

    Args:
        user_id (int): The ID of the user.

    Returns:
        tuple: A tuple containing the total amount earned overall and the total amount earned in the current month.
    """
    
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Filter out transactions with corresponding records in the Payment table with payment_type 'credit-wallet'
    subquery_filter = ~Transaction.key.in_(
        db.session.query(Transaction.key).join(
            Payment, Transaction.key == Payment.key
        ).filter(
            Payment.payment_type == 'credit-wallet'
        ).subquery()
    )

    # Calculate total amount earned by the current user
    total_earned_overall = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.trendit3_user_id == user_id,
        Transaction.transaction_type == TransactionType.CREDIT,
        subquery_filter
    ).scalar() or 0.0

    # Calculate total amount earned by the current user in the current month
    total_earned_current_month = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.trendit3_user_id == user_id,
        Transaction.transaction_type == TransactionType.CREDIT,
        subquery_filter,
        db.extract('month', Transaction.created_at) == current_month,
        db.extract('year', Transaction.created_at) == current_year
    ).scalar() or 0.0

    return total_earned_overall, total_earned_current_month