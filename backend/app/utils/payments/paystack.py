"""
@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
"""

import requests
from flask import json
from sqlalchemy.exc import ( DataError, DatabaseError )

from ...extensions import db
from.exceptions import TransactionMissingError
from ...models import Payment, Transaction, TransactionType, Withdrawal, Trendit3User, TaskPaymentStatus
from ...utils.helpers.payment_helpers import initialize_payment, credit_wallet, initiate_transfer
from ...utils.helpers.basic_helpers import console_log, log_exception, generate_random_string
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.task_helpers import get_task_by_key
from config import Config


auth_headers ={
    "Authorization": "Bearer {}".format(Config.PAYSTACK_SECRET_KEY),
    "Content-Type": "application/json"
}

def initialize_paystack_payment(amount: int, payload: dict, payment_type: str, user: Trendit3User) -> tuple[bool, dict]:
    try:
        
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


def verify_paystack_payment(data):
    """ Verify payment with Paystack"""
    
    reference = data.get('reference') # Extract reference from request body
    
    paystack_response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=auth_headers)
    status_code = int(paystack_response.status_code)
    response_data = paystack_response.json()
    
    if not response_data['status']:
        return error_response(response_data['message'], 404)
    
    # Extract needed data
    amount = float(response_data['data']['amount']) / 100  # Convert from kobo to naira
    payment_status = response_data['data']['status'].lower()
    
    transaction = Transaction.query.filter_by(key=reference).first()
    payment = Payment.query.filter_by(key=reference).first()
    
    if not transaction:
        raise TransactionMissingError
    
    user_id = transaction.trendit3_user_id
    payment_type = payment.payment_type
    
    trendit3_user = transaction.trendit3_user
    if trendit3_user is None:
        return error_response('User does not exist', 404)
    
    msg = ""
    extra_data = {'payment_status': payment_status}
    
    # if verification was successful
    if 'status' in response_data:
        if response_data['status'] and payment_status == 'success':
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
                        msg = f'Error crediting wallet. Please Try To Verify Again: {e}'
                        return error_response(msg, 400)
                            
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
            
            status = True
        elif response_data['status'] and response_data['data']['status'].lower() == 'abandoned':
            # Payment was not completed
            if transaction.status.lower() != 'abandoned':
                transaction.update(status='abandoned') # update the status
                payment.update(status='abandoned') # update the status
                
            msg = f"Abandoned: {response_data['data']['gateway_response']}"
                
        else:
            # Payment was not successful
            if transaction.status.lower() != 'failed':
                transaction.update(status='failed') # update the status
                payment.update(status='failed') # update the status
                    
            msg = 'Payment verification failed: ' + response_data['message']
    else:
        status = False
        extra_data = response_data
    
    extra_data.update({'user_data': trendit3_user.to_dict(), 'status_code': status_code})
    result = {
        'msg': msg,
        'status': status,
        'extra_data': extra_data
    }
    return result

