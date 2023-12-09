import random, string, secrets, logging, time
from flask import abort
from app.extensions import db
from slugify import slugify

from app.models.item import Item
from app.exceptions import UniqueSlugError


def paginate_results(request, results, result_per_page=10):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * result_per_page
    end = start + result_per_page

    the_results = [result.to_dict() for result in results]
    current_results = the_results[start:end]

    return current_results

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


def get_object_by_slug(model: db.Model, slug: str):
    """
    Retrieve an object from the database based on its unique slug.

    Parameters:
    - model (db.Model): The SQLAlchemy model class representing the database table.
    - slug (str): The unique slug used to identify the object.

    Returns:
    db.Model or None: The object with the specified slug if found, or None if not found.

    Usage:
    Call this function with the model class and the slug of the object you want to retrieve.
    Returns the object if found, or None if no matching object is present in the database.
    """
    return model.query.filter_by(slug=slug).first()

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
    base_slug = slugify(name)
    slug = base_slug
    timestamp = str(int(time.time() * 1000))
    counter = 1
    max_attempts = 4  # maximum number of attempts to create a unique slug
    
    # when updating, Check existing obj name is the same
    if existing_obj:
        if existing_obj.name == name:
            return existing_obj.slug

    model_mapping = {
        'item': Item,
        # Add more mappings for other types as needed
        # 'product': Product,
        # 'task': Task,
    }
    
    # Check if slug already exists in database
    # Use the helper function with the dynamically determined model type
    is_obj = get_object_by_slug(model_mapping.get(type), slug)
    
    while is_obj:
        if counter > max_attempts:
            raise UniqueSlugError(name, type, msg=f"Unable to create a unique item slug after {max_attempts} attempts.")
        
        suffix = generate_random_string(5)
        slug = f"{base_slug}-{suffix}-{timestamp}" if counter == 2 else f"{base_slug}-{suffix}"

        # Check if the combination of slug and suffix is also taken
        # Use the helper function with the dynamically determined model type
        is_obj = get_object_by_slug(model_mapping.get(type), slug)
        
        counter += 1

    return slug


def console_log(label='Label', data=None):
    
    print(f'\n\n{label:-^50}\n', data, f'\n{"//":-^50}\n\n')


def log_exception(label='EXCEPTION', data='Nothing'):
    logging.exception(f"\n\n{label:-^50}\n An exception occurred during registration.\n", str(data)) # Log the error details for debugging