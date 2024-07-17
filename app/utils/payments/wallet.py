'''
@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
from decimal import Decimal

from ...extensions import db
from ...models import Payment, Transaction, TransactionType, Withdrawal, Trendit3User
from ...utils.helpers.basic_helpers import console_log, log_exception, generate_random_string
from ...utils.helpers.mail_helpers import send_other_emails, send_transaction_alert_email


def debit_wallet(user_id: int, amount: int, payment_type=None) -> float:
    user: Trendit3User = Trendit3User.query.get(user_id)
    
    if user is None:
        raise ValueError("User not found.")
    
    amount = Decimal(amount)
    wallet = user.wallet

    if wallet is None:
        raise ValueError("User does not have a wallet.")

    current_balance = wallet.balance
    if current_balance < amount:
        raise ValueError("Insufficient balance.")

    service_paid_for = "New Social Task Order" if payment_type == "task-creation" else "Product From The Marketplace"
    
    try:
        # Debit the wallet
        wallet.balance -= amount
        key = generate_random_string(16)
        payment = Payment(key=key, amount=amount, payment_type=payment_type, payment_method='wallet', status='complete', trendit3_user=user)
        transaction = Transaction(key=key, amount=amount, transaction_type=TransactionType.DEBIT, status='complete', description=f'payment for {service_paid_for}', trendit3_user=user)
        
        db.session.add_all([payment, transaction])
        db.session.commit()
        
        send_transaction_alert_email("debit", user.email, reason=service_paid_for, amount=amount) # send debit alert to user's mail
        return wallet.balance
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e


def credit_wallet(user_id: int, amount: int | float | Decimal, credit_type="task-performance") -> Decimal:
    user: Trendit3User = Trendit3User.query.get(user_id)
    
    if user is None:
        raise ValueError("User not found.")
    
    wallet = user.wallet

    if wallet is None:
        raise ValueError("User does not have a wallet.")

    try:
        # Credit the wallet
        wallet.balance += Decimal(amount)
        db.session.commit()
        
        if credit_type in ["task-performance", "funded-wallet"]:
            send_transaction_alert_email("credit", user.email, reason=credit_type, amount=amount)
        
        return wallet.balance
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e

