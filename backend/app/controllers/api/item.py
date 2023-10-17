import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.models.item import Item
from app.utils.helpers.item_helpers import save_item
from app.utils.helpers.payment_helpers import is_paid


class ItemController:
    @staticmethod
    def get_items():
        error = False
        try:
            items = Item.query.all()
            item_list = [item.to_dict() for item in items]
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error fetching Items from the database"
            logging.exception("An exception occurred during fetching Items.\n", str(e))
        if error:
            return jsonify({
                "status": "failed",
                "status_code": status_code,
                "message": msg,
            }), status_code
        else:
            return jsonify({
                "status": "success",
                "status_code": 200,
                "message": "Items fetched successfully",
                "items": item_list
            }), 200


    @staticmethod
    def create_item():
        error = False
        
        try:
            data = request.form.to_dict()
            user_id = get_jwt_identity()
            
            if not is_paid(user_id, 'item_upload'):
                return jsonify({
                    "status": "failed",
                    "status_code": 403,
                    'message': 'Please make the required payment to upload items.'
                }), 403

            new_item = save_item(data) # Save the item
            if new_item:
                status_code = 200
                msg = "Item Created successfully"
                item = new_item.to_dict()
            else:
                error = True
                status_code = 500
                msg = "Error creating new item"
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error creating new item"
            logging.exception("An exception occurred during creation of Item.\n", str(e))
        
        if error:
            return jsonify({
                "status": "failed",
                "status_code": status_code,
                "message": msg,
            }), status_code
        else:
            return jsonify({
                "status": "success",
                "status_code": status_code,
                "message": msg,
                "item": item
            }), status_code


    @staticmethod
    def update_item(item_id):
        error = False
        
        try:
            data = request.form.to_dict()
            user_id = get_jwt_identity()
            
            item = Item.query.get(item_id)
            
            if item is None:
                return jsonify({
                    "status": "failed",
                    "status_code": 404,
                    'message': 'Item not found'
                }), 404
            
            if item.seller_id != user_id:
                return jsonify({
                    "status": "failed",
                    "status_code": 403,
                    'message': 'You are not authorized to update this item'
                }), 403
            
            # Update the item properties as needed
            updated_item = save_item(data, item_id)
            if updated_item:
                status_code = 200
                msg = "Item Updated successfully"
                item = updated_item.to_dict()
            else:
                error = True
                status_code = 500
                msg = "Error updating item"
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error updating item"
            logging.exception("An exception occurred during updating of Item.\n", str(e))
        
        if error:
            return jsonify({
                "status": "failed",
                "status_code": status_code,
                "message": msg,
            }), status_code
        else:
            return jsonify({
                "status": "success",
                "status_code": status_code,
                "message": msg,
                "item": item
            }), status_code
    
