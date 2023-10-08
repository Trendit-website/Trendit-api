from app.models.payment import Payment
from app.models.user import Trendit3User

def is_paid(user_id, payment_type):
    """
    Checks whether a user has paid a specific type of fee.

    Args:
        user_id (int): The ID of the user to check.
        payment_type (str): The type of payment to check. Can be 'activation_fee' or 'item_upload'.

    Returns:
        bool: True if the user has paid the specified fee, False otherwise.
    """
    
    paid = False
    
    Trendit3_user = Trendit3User.query.get(user_id)
    
    if payment_type == 'activation_fee':
        paid = Trendit3_user.membership.activation_fee_paid
    elif payment_type == 'item_upload':
        paid = Trendit3_user.membership.item_upload_paid
    
    return paid
