from app.routes.api import bp
from app.controllers.api.payment import PaymentController

@bp.route('/payment', methods=['POST'])
def make_payment():
    return PaymentController.process_payment()

@bp.route('/payment/verify', methods=['POST'])
def verify_payment():
    return PaymentController.verify_payment()

@bp.route('/payment/history', methods=['GET'])
def payment_history():
    return PaymentController.get_payment_history()
