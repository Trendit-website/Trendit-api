from flask_jwt_extended import jwt_required, get_jwt_identity

from app.routes.api import bp
from app.controllers.api import ItemController


@bp.route('/items', methods=['GET'])
def list_items():
    return ItemController.get_items()



@bp.route('/items/new', methods=['POST'])
@jwt_required()
def create_item():
    return ItemController.create_item()



@bp.route('/items/update/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    return ItemController.update_item(item_id)

