from flask import request, url_for, abort


def urlParts():
    '''
    this splits the currents url into different parts
    and returns the different parts in an array
    '''
    url = request.base_url
    theUrlParts =url.split('/')
    
    return theUrlParts

def get_or_404(query):
    result = query.one_or_none()
    if result is None:
        abort(404)
    
    return result

def intOrNone(s):
    try:
        return int(s)
    except:
        return None
