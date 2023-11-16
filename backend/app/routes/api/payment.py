from flask_jwt_extended import jwt_required

from app.routes.api import bp
from app.controllers.api.payment import PaymentController

@bp.route('/payment/<payment_type>', methods=['POST'])
@jwt_required()
def make_payment(payment_type):
    """
    Processes a payment for a user.

    Returns:
        json: A JSON object containing the status of the payment, a status code, and a message.
    """
    return PaymentController.process_payment(payment_type)


@bp.route('/payment/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """
    Verifies a payment for a user.

    Returns:
        json: A JSON object containing the status of the verification, a status code, and a message.
    """
    return PaymentController.verify_payment()


@bp.route('/payment/history', methods=['GET'])
@jwt_required()
def payment_history():
    """
    Fetches the payment history for a user.

    Returns:
        json: A JSON object containing the status of the request, a status code, and the payment history.
    """
    return PaymentController.get_payment_history()


@bp.route('/payment/webhook', methods=['POST'])
def payment_hook():
    """
    Handles a webhook for a payment.

    Returns:
        json: A JSON object containing the status of the webhook handling.
    """
    return PaymentController.handle_webhook()
