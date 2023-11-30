import sys
from flask import request, jsonify, current_app
from sqlalchemy import desc, func, text
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.item import Item
from app.utils.helpers.basic_helpers import generate_slug
from app.utils.helpers.media_helpers import save_media


def item_check(item_id):
    item = Item.query.get(item_id)
    
    if item is None:
        return jsonify({
            "status": "failed",
            "status_code": 404,
            "message": "Item not found"
        }), 404
    else:
        pass

def save_item(data, item_id=None):
    """
    Function: save_item

    Description:
    Saves a new or updated item to the database based on json data. If an item with the same ID already exists in the database, it updates the existing item. Otherwise, it creates a new item with a unique slug.

    Parameters:
    - data: A JSON that contains data for the item, including name, description, price, category, brand_name, size, and color.
    - item_id: An optional parameter used to determine if an item already exist, and then update that item if it does. The default value is None.

    Returns: None

    Raises:
    - An exception if there is an error while saving the item, and rolls back the database transaction. The exception is logged with the Flask logger and re-raised.
    """
    try:
        item_type = data.get('item_type', '')
        name = data.get('name', '')
        description = data.get('description', '')
        item_img = request.files['item_img']
        price = data.get('price', '')
        category = data.get('category', '')
        brand_name = data.get('brand_name', '')
        size = data.get('size', '')
        color = data.get('color', '')
        material = data.get('material', '')
        phone = data.get('phone', '')
        
        item = None
        if item_id:
            item = Item.query.get(item_id)
        
        if item_img.filename != '':
            try:
                item_img = save_media(item_img) # This saves image file, saves the path in db and return the id of the image
            except Exception as e:
                current_app.logger.error(f"An error occurred while saving image for item {data.get('name')}: {str(e)}")
                return None
        elif item_img.filename == '' and item:
            if item.item_img:
                item_img = item.item_img
            else:
                item_img = None
        else:
            item_img = None
        
        if item:
            item.slug = generate_slug(name, 'item', item)
            item.item_type = item_type
            item.name = name
            item.description = description
            item.item_img = item_img
            item.price = price
            item.category = category
            item.brand_name = brand_name
            item.size = size
            item.color = color
            item.material = material
            item.phone = phone
            
            item.update()
            return item
        else:
            slug = generate_slug(name, 'item')
            new_item = Item(item_type=item_type, name=name, description=description, item_img=item_img, price=price, category=category, brand_name=brand_name, size=size, color=color, material=material, phone=phone, slug=slug, seller_id=get_jwt_identity())
            
            new_item.insert()
            return new_item
    except Exception as e:
        current_app.logger.error(f"An error occurred while saving item {data.get('name')}: {str(e)}")
        db.session.rollback()
        print(f'\n\n{"sys excInfo":-^30}\n', sys.exc_info(), f'\n{"///":-^30}\n\n')
        return None
