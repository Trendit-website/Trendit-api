import random, string
from flask import request, url_for, abort


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