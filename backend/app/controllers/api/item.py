import logging
from flask import request
from flask_jwt_extended import get_jwt_identity

from config import Config
from app.models.item import Item
from app.utils.helpers.item_helpers import save_item, fetch_item
from app.utils.helpers.payment_helpers import is_paid
from app.utils.helpers.response_helpers import error_response, success_response


class ItemController:
    @staticmethod
    def get_items():
        error = False
        try:
            page = request.args.get("page", 1, type=int)
            items_per_page = int(Config.ITEMS_PER_PAGE)
            pagination = Item.query.order_by(Item.created_at.desc()).paginate(page=page, per_page=items_per_page, error_out=False)
            
            items = pagination.items
            current_items = [item.to_dict() for item in items]
            extra_data = {
                "total": pagination.total,
                "all_items": current_items,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not items:
                return success_response('There are no product or services yet', 200, extra_data)
                
        except Exception as e:
            error = True
            status_code = 500
            msg = f"Error fetching Products & Services from the database: {str(e)}"
            logging.exception("An exception occurred during fetching Items.\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response('Products & Services fetched successfully', 200, extra_data)


    @staticmethod
    def create_item():
        error = False
        
        try:
            data = request.form.to_dict()
            item_type = data.get('item_type', '')
            user_id = get_jwt_identity()
            
            if not is_paid(user_id, 'membership-fee'):
                return error_response('Membership fee has not been paid yet', 403)

            new_item = save_item(data) # Save the item
            if new_item:
                status_code = 201
                msg = f"{item_type} Created successfully"
                item = new_item.to_dict()
            else:
                error = True
                status_code = 500
                msg = f"Error creating new {item_type}"
        except Exception as e:
            error = True
            status_code = 500
            msg = f"Error creating new {item_type}"
            logging.exception("An exception occurred during creation of Item.\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, {"item": item})


    @staticmethod
    def update_item(item_id_slug):
        error = False
        
        try:
            item = fetch_item(item_id_slug)
            
            data = request.form.to_dict()
            item_type = data.get('item_type', item.item_type)
            user_id = get_jwt_identity()
            
            
            if item is None:
                return error_response('Item not found', 404)
            
            if item.seller_id != user_id:
                return error_response(f'You are not authorized to update this {item.item_type}', 403)
            
            # Update the item properties as needed
            updated_item = save_item(data, item_id_slug)
            if updated_item:
                status_code = 200
                msg = f"{item_type} Updated successfully"
                item = updated_item.to_dict()
                extra_data = {
                    "item": item
                }
            else:
                error = True
                status_code = 500
                msg = f"Error updating {item.item_type}"
        except Exception as e:
            error = True
            status_code = 500
            msg = f"Error updating {item.item_type}"
            logging.exception("An exception occurred during updating of Item.\n", str(e))
        
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)


    @staticmethod
    def get_single_item(item_id_slug):
        error = False
        try:
            item = fetch_item(item_id_slug)
            if item is None:
                return error_response('Product/Service not found', 404)
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error fetching Product/Service"
            logging.exception("An exception occurred during fetching of Item.\n", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(f'{item.item_type} fetched successfully', 200, {"item": item.to_dict()})


    @staticmethod
    def delete_item(item_id_slug):
        error = False
        try:
            item = fetch_item(item_id_slug)
            if item is None:
                return error_response('Product/Service not found', 404)
            
            item_type = item.item_type
            item.delete()
        except Exception as e:
            error = True
            status_code = 500
            msg = "Error deleting Product/Service"
            logging.exception("An exception occurred during deletion of Item:", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(f'{item_type} deleted successfully', 200)