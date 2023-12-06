from flask_jwt_extended import jwt_required, get_jwt_identity

from app.routes.api import bp
from app.controllers.api import ItemInteractionsController


@bp.route('/items/<item_id_slug>/like', methods=['POST'])
@jwt_required()
def like_item(item_id_slug):
    return ItemInteractionsController.like_item(item_id_slug)



@bp.route('/items/<item_id_slug>/share', methods=['POST'])
@jwt_required()
def share_item(item_id_slug):
    return ItemInteractionsController.share_item(item_id_slug)



# Route for viewing an item (increment view count)
@bp.route('/items/<item_id_slug>/view', methods=['POST'])
def view_item(item_id_slug):
    return ItemInteractionsController.view_item(item_id_slug)



# Route for adding a comment to an item
@bp.route('/items/<item_id_slug>/comment', methods=['POST'])
@jwt_required()
def add_comment(item_id_slug):
    return ItemInteractionsController.add_comment(item_id_slug)

