"""
@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
"""

import requests, hmac, hashlib
from flask import json, request, jsonify
from sqlalchemy.exc import ( DataError, DatabaseError )

from ...extensions import db
from ...models import Payment, Transaction, TransactionType, Withdrawal, Trendit3User, TaskPaymentStatus
from ...utils.helpers.payment_helpers import initialize_payment, credit_wallet, initiate_transfer
from ...utils.helpers.basic_helpers import console_log, log_exception, generate_random_string
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.task_helpers import get_task_by_key
from ...utils.helpers.mail_helpers import send_other_emails
from .exceptions import TransactionMissingError, CreditWalletError, SignatureError
from config import Config



auth_headers ={
    "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
    "Content-Type": "application/json"
}

def initialize_paystack_payment(amount: int, payload: dict, payment_type: str, user: Trendit3User) -> dict:
    try:
        
        response = requests.post(Config.PAYSTACK_INITIALIZE_URL, headers=auth_headers, data=json.dumps(payload))
        status_code = int(response.status_code)
        console_log('response', response)
        
        response_data = response.json()
        console_log('response_data', response_data)
        
        if 'status' in response_data:
            if response_data['status']:
                tx_ref=response_data['data']['reference'] # transaction reference
                transaction = Transaction(key=tx_ref, amount=amount, transaction_type=TransactionType.PAYMENT, description=f'{payment_type} payment', status='pending', trendit3_user=user)
                payment = Payment(key=tx_ref, amount=amount, payment_type=payment_type, payment_method=Config.PAYMENT_GATEWAY.lower(),status='pending', trendit3_user=user)
                db.session.add_all([transaction, payment])
                db.session.commit()
                
                authorization_url = response_data['data']['authorization_url'] # Get authorization URL from response
                msg = 'Payment initialized'
                success = True
                extra_data = {
                    'authorization_url': authorization_url,
                    'payment_type': payment_type,
                    "metadata": payload['metadata'],
                    "status_code": status_code
                }
            else:
                msg = 'Payment initialization failed'
                success = False
                response_data.update({"metadata": payload['metadata'], "status_code": status_code})
                extra_data = response_data
        else:
            msg = 'Payment initialization failed'
            success = False
            removed_message = response_data.pop('message') if 'message' in response_data else ''
            extra_data = response_data
        
        console_log('extra_data', extra_data)
        result = {
            'msg': msg,
            'success': success,
            'extra_data': extra_data
        }
    except (DataError, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e
    
    return result


def verify_paystack_payment(data):
    """ Verify payment with Paystack"""
    
    try:
        reference = data.get('reference') # Extract reference from request body
        
        paystack_response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=auth_headers)
        status_code = int(paystack_response.status_code)
        response_data = paystack_response.json()
        
        console_log('response_data', response_data)
        
        if 'status' in response_data:
            msg = ""
            payment_status = response_data['data']['status'].lower()
            extra_data = {'payment_status': payment_status}
            
            transaction = Transaction.query.filter_by(key=reference).first()
            payment = Payment.query.filter_by(key=reference).first()
            
            if not transaction:
                raise TransactionMissingError
            
            user_id = transaction.trendit3_user_id
            trendit3_user = transaction.trendit3_user
            payment_type = payment.payment_type
            
            # if verification was successful
            if response_data['status'] and payment_status == 'success':
                # Extract needed data
                amount = float(response_data['data']['amount']) / 100  # Convert from kobo to naira
                msg = f"Payment verified successfully: {response_data['data']['gateway_response']}"
                
                if transaction.status.lower() != 'complete':
                    # Record the payment and transaction in the database
                    with db.session.begin_nested():
                        transaction.status = 'complete'
                        payment.status = 'complete'
                        db.session.commit()
                        
                    # Update user's membership status in the database
                    if payment_type == 'membership-fee':
                        trendit3_user.membership_fee(paid=True)
                        membership_fee_paid = trendit3_user.membership.membership_fee_paid
                        msg = 'Payment verified successfully and Account has been activated'
                        extra_data.update({'membership_fee_paid': membership_fee_paid})
                            
                    elif payment_type == 'task-creation':
                        task_key = response_data['data']['metadata']['task_key']
                        task = get_task_by_key(task_key)
                        task.update(payment_status=TaskPaymentStatus.COMPLETE)
                        task_dict = task.to_dict()
                        msg = 'Payment verified and Task has been created successfully'
                        extra_data.update({'task': task_dict})
                            
                    elif payment_type == 'credit-wallet':
                        # Credit user's wallet
                        try:
                            credit_wallet(user_id, amount)
                        except ValueError as e:
                            raise CreditWalletError(f'Error crediting wallet. Please Try To Verify Again: {e}')
                        
                        msg = 'Wallet Credited successfully'
                    
                elif transaction.status.lower() == 'complete':
                    if payment_type == 'membership-fee':
                        msg = 'Payment Completed successfully and Account is already activated'
                        extra_data.update({'membership_fee_paid': trendit3_user.membership.membership_fee_paid,})
                            
                    elif payment_type == 'task-creation':
                        task_key = response_data['data']['metadata']['task_key']
                        task = get_task_by_key(task_key)
                        task_dict = task.to_dict()
                        msg = 'Payment Completed and Task has already been created successfully'
                        extra_data.update({'task': task_dict})
                            
                    elif payment_type == 'credit-wallet':
                        msg = 'Payment Completed and Wallet already credited'
                
                success = True
            elif response_data['status'] and response_data['data']['status'].lower() == 'abandoned':
                # Payment was not completed
                if transaction.status.lower() != 'abandoned':
                    transaction.update(status='abandoned') # update the status
                    payment.update(status='abandoned') # update the status
                    
                msg = f"Abandoned: {response_data['data']['gateway_response']}"
                success = False
            
            else:
                # Payment was not successful
                if transaction.status.lower() != 'failed':
                    transaction.update(status='failed') # update the status
                    payment.update(status='failed') # update the status
                        
                msg = 'Payment verification failed: ' + response_data['message']
                success = False
            
            extra_data.update({'user_data': trendit3_user.to_dict(), 'status_code': status_code})
        else:
            msg = 'An error occurred verifying payment: Contact the admin'
            success = False
            removed_message = response_data.pop('message')
            extra_data = response_data
        
        console_log('extra_data', extra_data)
        
        result = {
            'msg': msg,
            'status': success,
            'extra_data': extra_data
        }
    except (DataError, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e
    
    return result


def paystack_webhook():
    try:
        signature = request.headers.get('X-Paystack-Signature') # Get the signature from the request headers
        secret_key = Config.PAYSTACK_SECRET_KEY # Get Paystack secret key
        
        data = json.loads(request.data) # Get the data from the request
        console_log('DATA', data)
        
        # Create hash using the secret key and the data
        hash = hmac.new(secret_key.encode(), msg=request.data, digestmod=hashlib.sha512)
        
        if not signature:
            raise SignatureError(f'No signature in headers')
        
        # Verify the signature
        if not hmac.compare_digest(hash.hexdigest(), signature):
            raise SignatureError(f'Invalid signature')
        
        # Extract needed data
        amount = float(data['data']['amount']) / 100  # Convert from kobo to naira
        reference = f"{data['data']['reference']}"
        
        transaction = Transaction.query.filter_by(key=reference).first()
        payment = Payment.query.filter_by(key=reference).first()
        if transaction:
            user_id = transaction.trendit3_user_id
            payment_type = payment.payment_type
            trendit3_user = transaction.trendit3_user

            # Check if this is a successful payment event
            if data['event'] == 'charge.success':
                
                if transaction.status.lower() != 'complete':
                    # Record the payment and transaction in the database
                    transaction.update(status='complete')
                    payment.update(status='complete')
                
                    # Update user's membership status in the database
                    if payment_type == 'membership-fee':
                        trendit3_user.membership_fee(paid=True)
                        try:
                            send_other_emails(trendit3_user.email, amount=amount) # send email
                        except Exception as e:
                            raise Exception('Error occurred sending Email')
                    
                    elif payment_type == 'task-creation':
                        task_key = data['data']['metadata']['task_key']
                        task = get_task_by_key(task_key)
                        task.update(payment_status=TaskPaymentStatus.COMPLETE)
                    
                    elif payment_type == 'credit-wallet':
                        # Credit user's wallet
                        try:
                            credit_wallet(user_id, amount)
                            send_other_emails(trendit3_user.email, email_type='credit', amount=amount) # send credit alert to user's email
                        except ValueError as e:
                            raise ValueError(f'Error crediting wallet: {e}')
                        except Exception as e:
                            raise Exception(f'Error occurred sending Email or crediting wallet: {e}')
                
                result = {
                    "success": True,
                    "status_code": 200
                }
                
            elif data['event'] == 'charge.abandoned':
                # Payment was not completed
                if transaction.status.lower() != 'abandoned':
                    transaction.update(status='abandoned') # update the status
                    payment.update(status='abandoned') # update the status
                
                result = {
                    "success": False,
                    "status_code": 200
                }
            else:
                # Payment was not successful
                if transaction.status.lower() != 'failed':
                    transaction.update(status='failed') # update the status
                    payment.update(status='failed') # update the status
                
                result = {
                    "success": False,
                    "status_code": 200
                }
        else:
            result = {
                "success": False,
                "status_code": 404
            }
    except SignatureError as e:
        fund_wallet = credit_wallet(user_id, amount) if data['event'] == 'charge.success' else False
        raise e
    except (DataError, DatabaseError) as e:
        fund_wallet = credit_wallet(user_id, amount) if data['event'] == 'charge.success' else False
        raise e
    except Exception as e:
        fund_wallet = credit_wallet(user_id, amount) if data['event'] == 'charge.success' else False
        raise e
    
    return result

