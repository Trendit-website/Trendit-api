import sys
from flask import request, jsonify, current_app
from werkzeug.exceptions import BadRequestKeyError
from sqlalchemy import or_
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.item import Item
from app.exceptions import UniqueSlugError
from app.utils.helpers.basic_helpers import generate_slug, console_log
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


def save_item(data, item_id_slug=None):
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
        item = None
        if item_id_slug:
            item = fetch_item(item_id_slug)
        
        
        user_id = int(get_jwt_identity())
        country = data.get('country', item.country if item else '')
        state = data.get('state', item.state if item else '')
        
        city = data.get('city', item.city if item else '')
        item_type = data.get('item_type', item.item_type if item else '')
        name = data.get('name', item.name if item else '')
        
        description = data.get('description', item.description if item else '')
        item_img = request.files['item_img']
        price = data.get('price', item.price if item else '')
        
        category = data.get('category', item.category if item else '')
        brand_name = data.get('brand_name', item.brand_name if item else '')
        size = data.get('size', item.size if item else '')
        
        color = data.get('color', item.color if item else '')
        material = data.get('material', item.material if item else '')
        phone = data.get('phone', item.phone if item else '')
        
        
        if item_img.filename != '':
            try:
                item_img_id = save_media(item_img) # This saves image file, saves the path in db and return the id of the image
            except Exception as e:
                current_app.logger.error(f"An error occurred while saving image for item {data.get('name')}: {str(e)}")
                return None
        elif item_img.filename == '' and item:
            if item.item_img_id:
                item_img_id = item.item_img_id
            else:
                item_img_id = None
        else:
            item_img_id = None
        
        if item:
            slug = generate_slug(name, 'item', item)
            
            item.update(item_type=item_type, name=name, description=description, item_img_id=item_img_id, price=price, category=category, brand_name=brand_name, slug=slug, size=size, color=color, material=material, phone=phone, country=country, state=state, city=city)
            
            return item
        else:
            slug = generate_slug(name, 'item')
            new_item = Item.create_item(item_type=item_type, name=name, description=description, price=price, category=category, brand_name=brand_name, size=size, color=color, material=material, phone=phone, item_img_id=item_img_id, country=country, state=state, city=city, slug=slug, seller_id=user_id)
            
            return new_item
    except BadRequestKeyError as e:
        # Handle the case where 'item_img' is not present in the request
        current_app.logger.error(f"An error occurred while saving item ==> Missing item_img field in the request: {str(e)}")
        return None
    except UniqueSlugError as e:
        current_app.logger.error(f"An error occurred while saving item: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"An error occurred while saving item {data.get('name')}: {str(e)}")
        db.session.rollback()
        console_log('sys excInfo', sys.exc_info())
        return None


def fetch_item(item_id_slug):
    """
    Fetches an item from the database based on either its ID or slug.

    Parameters:
    - item_id_slug (int or str): The ID or slug of the item to fetch. 
        - If an integer, the function fetches the item by ID; 
        - if a string, it fetches the item by slug.

    Returns:
    - Item or None: The fetched item if found, or None if no item matches the provided ID or slug.
    """
    try:
        # Check if item_id_slug is an integer
        item_id_slug = int(item_id_slug)
        # Fetch the item by id
        item = Item.query.filter_by(id=item_id_slug).first()
    except ValueError:
        # If not an integer, treat it as a string
        item = Item.query.filter_by(slug=item_id_slug).first()

    if item:
        return item
    else:
        return None
