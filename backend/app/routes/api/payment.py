from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api.payment import PaymentController

@api.route('/payment/<payment_type>', methods=['POST'])
@jwt_required()
def make_payment(payment_type):
    """
    Processes a payment for a user.

    Returns:
        json: A JSON object containing the status of the payment, a status code, and a message.
    """
    return PaymentController.process_payment(payment_type)


@api.route('/payment/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """
    Verifies a payment for a user.

    Returns:
        json: A JSON object containing the status of the verification, a status code, and a message.
    """
    return PaymentController.verify_payment()


@api.route('/payment/history', methods=['GET'])
@jwt_required()
def payment_history():
    """
    Fetches the payment history for a user.

    Returns:
        json: A JSON object containing the status of the request, a status code, and the payment history.
    """
    return PaymentController.get_payment_history()


@api.route('/payment/webhook', methods=['POST'])
def payment_hook():
    """
    Handles a webhook for a payment.

    Returns:
        json: A JSON object containing the status of the webhook handling.
    """
    return PaymentController.handle_webhook()


@api.route('/payment/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    """
    Process for users to Withdraw money into their bank accounts.

    Returns:
        json: A JSON object containing the status of the withdrawal, a status code, and a message.
    """
    return PaymentController.withdraw()


@api.route('/payment/withdraw-approval', methods=['POST'])
def withdraw_approval_webhook():
    return PaymentController.withdraw_approval_webhook()


@api.route('/payment/withdraw/verify', methods=['POST'])
@jwt_required()
def verify_withdraw():
    return PaymentController.verify_withdraw()