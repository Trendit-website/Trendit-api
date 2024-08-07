from flask import Flask
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from ...utils.payments.rates import convert_amount
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User


def send_async_transaction_alert_email(app: Flask, tx_type: str, user_email: str, reason: str, amount=None) -> None:
    with app.app_context():
        user: Trendit3User = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        username: str = user.username if user else ''
        firstname: str = user.profile.firstname if user else ''
        currency_code: str = user.wallet.currency_code
        amount: str = convert_amount(amount, currency_code)
        
        console_log("amount", f"{currency_code} {amount}")
        
        subject = 'Wallet Debited'
        template = render_template(
            "mail/debit-alert.html",
            user=user,
            user_email=user_email,
            username=username,
            currency_code=currency_code,
            amount=amount,
            reason=reason
        )
        if tx_type == "credit":
            subject = 'Wallet Credited'
            template = render_template(
                "mail/credit-alert.html",
                user=user,
                user_email=user_email,
                firstname=firstname,
                username=username,
                currency_code=currency_code,
                amount=amount,
                reason=reason
            )
        
        msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING '{tx_type} transaction' MAIL", e)

def send_transaction_alert_email(user_email, reason, amount, tx_type="debit"):
    Thread(target=send_async_transaction_alert_email, args=(current_app._get_current_object(), tx_type, user_email, reason, amount)).start()
