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
        
        send_transaction_alert_email(user.email, reason=service_paid_for, amount=amount, tx_type="debit") # send debit alert to user's mail
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
            send_transaction_alert_email(user.email, reason=credit_type, amount=amount, tx_type="credit")
        
        return wallet.balance
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e


def refund_to_wallet(user_id: int, amount: int | float | Decimal, reason="task-rejection") -> Decimal:
    """
    This function processes a refund for a user with a 1.5% fee deduction.

    Args:
        user_id: The ID of the user to be refunded.
        amount: The original amount paid for the task.

    Returns:
        wallet ballance if the refund was successful, raises exception otherwise.
    """
    user: Trendit3User = Trendit3User.query.get(user_id)
    
    if user is None:
        raise ValueError("User not found.")
    
    wallet = user.wallet

    if wallet is None:
        raise ValueError("User does not have a wallet.")
    
    fee_percentage = Decimal('0.015')  # Represents 1.5% as a decimal
    fee = amount * fee_percentage
    refund_amount = amount - fee
    
    try:
        # Credit the wallet
        wallet.balance += Decimal(refund_amount)
        db.session.commit()
        
        if reason in ["task-rejection", "failed-payment"]:
            send_transaction_alert_email(user.email, reason=reason, amount=refund_amount, tx_type="credit")
        
        return wallet.balance
    except Exception as e:
        # Handle the exception appropriately (rollback, log the error, etc.)
        db.session.rollback()
        raise e
