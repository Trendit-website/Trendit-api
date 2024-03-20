'''
This module defines basic helper functions for the Trendit³ Flask application.

These functions perform common tasks that are used throughout the application.

@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''
import random, string, secrets, logging, time
from threading import Thread
from flask import current_app, abort, request, render_template, url_for
from slugify import slugify
from flask_mail import Message

from ... import mail
from ...extensions import db
from ...models import Item
from ...exceptions import UniqueSlugError
from config import Config


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

class EmergencyAccessRestricted(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code

def check_emerge():
    emergency_mode = current_app.config.get('EMERGENCY_MODE', True)
    if request.endpoint not in ['api.enable_emerge', 'api.disable_emerge']:
        if emergency_mode:
            raise EmergencyAccessRestricted("Emergency access restrictions are in effect.")

def generate_random_string(length=8):
    """
    Generates a random string of specified length, consisting of lowercase letters and digits.

    Args:
        length (int): The desired length of the random string.

    Returns:
        str: A random string of the specified length.
    """
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_object_by_slug(model: object, slug: str):
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
    """
    Print a formatted message to the console for visual clarity.

    Args:
        label (str, optional): A label for the message, centered and surrounded by dashes. Defaults to 'Label'.
        data: The data to be printed. Can be of any type. Defaults to None.
    """

    print(f'\n\n{label:-^50}\n', data, f'\n{"//":-^50}\n\n')


def log_exception(label='EXCEPTION', data='Nothing'):
    """
    Log an exception with details to a logging handler for debugging.

    Args:
        label (str, optional): A label for the exception, centered and surrounded by dashes. Defaults to 'EXCEPTION'.
        data: Additional data to be logged along with the exception. Defaults to 'Nothing'.
    """

    logging.exception(f'\n\n{label:-^50}\n {str(data)} \n {"//":-^50}\n\n')  # Log the error details for debugging


def send_code_async_email(app, user_email):
    """
    Sends an email asynchronously.

    This function runs in a separate thread and sends an email to the user. 
    It uses the Flask application context to ensure the mail object works correctly.

    Args:
        app (Flask): The Flask application instance.
        user_email (str): The email address of the user.

    Returns:
        None
    """
    with app.app_context():
        subject = 'Verify Your Email'
        template = render_template("email/verify_email2.html")
        msg = Message(subject, sender=Config.MAIL_USERNAME, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f'An error occurred while sending email', e)

def send_mail_to_user():
    pass