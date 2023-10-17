from flask_jwt_extended import jwt_required, get_jwt_identity

from app.routes.api import bp
from app.controllers.api import ItemInteractionsController


@bp.route('/items/<int:item_id>/like', methods=['POST'])
@jwt_required()
def like_item(item_id):
    return ItemInteractionsController.like_item(item_id)



@bp.route('/items/<int:item_id>/share', methods=['POST'])
@jwt_required()
def share_item(item_id):
    return ItemInteractionsController.share_item(item_id)



# Route for viewing an item (increment view count)
@bp.route('/items/<int:item_id>/view', methods=['POST'])
def view_item(item_id):
    return ItemInteractionsController.view_item(item_id)



# Route for adding a comment to an item
@bp.route('/items/<int:item_id>/comment', methods=['POST'])
@jwt_required()
def add_comment(item_id):
    return ItemInteractionsController.add_comment(item_id)

