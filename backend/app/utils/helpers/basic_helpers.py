import random, string, secrets
from flask import request, url_for, abort
from slugify import slugify

from app.models.item import Item


def url_parts(url):
    """
    Splits a URL into its constituent parts.

    Args:
        url (str): The URL to split.

    Returns:
        list: A list of strings representing the parts of the URL.
    """
    
    theUrlParts =url.split('/')
    
    return theUrlParts

def get_or_404(query):
    """
    Executes a query and returns the result, or aborts with a 404 error if no result is found.

    Args:
        query (sqlalchemy.orm.query.Query): The SQLAlchemy query to execute.

    Returns:
        sqlalchemy.orm.query.Query: The result of the query.

    Raises:
        werkzeug.exceptions.NotFound: If the query returns no result.
    """
    
    result = query.one_or_none()
    if result is None:
        abort(404)
    
    return result

def int_or_none(s):
    """
    Converts a string to an integer, or returns None if the string cannot be converted.

    Args:
        s (str): The string to convert.

    Returns:
        int or None: The converted integer, or None if conversion is not possible.
    """
    
    try:
        return int(s)
    except:
        return None

def generate_random_string(length):
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_slug(name: str, type: str, existing_obj=None) -> str:
    """
    Generates a unique slug for a given name based on the type of object.

    Parameters:
    name (str): The name to generate a slug for.
    type (str): The type of object to generate a slug for (either 'product' or 'category').
    existing_obj (object): (Optional) The existing object to compare against to ensure uniqueness.
    

    Returns:
    str: The unique slug for the object.

    Usage:
    Call this function passing in the name and type of object you want to generate a slug for. 
    Optionally, you can pass in an existing object to compare against to ensure uniqueness.
    """
    slug = slugify(name)
    
    # Check if slug already exists in database
    if existing_obj:
        if existing_obj.name == name:
            return existing_obj.slug

    # Check if slug already exists in database
    if type == 'item':
        is_obj = Item.query.filter_by(slug=slug).first()
    
    if is_obj:
        suffix = secrets.token_urlsafe(3)[:6]
        slug = f"{slug}-{suffix}"

    return slug