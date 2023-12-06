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



@bp.route('/items/update/<item_id_slug>', methods=['PUT'])
@jwt_required()
def update_item(item_id_slug):
    return ItemController.update_item(item_id_slug)


@bp.route('/items/<item_id_slug>', methods=['GET'])
def get_single_item(item_id_slug):
    return ItemController.get_single_item(item_id_slug)


@bp.route('/items/delete/<item_id_slug>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id_slug):
    return ItemController.delete_item(item_id_slug)