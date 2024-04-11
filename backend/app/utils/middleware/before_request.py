import requests, socket
from flask import Flask, request, abort, current_app

from ..helpers import check_emerge, console_log
from ..helpers.response_helpers import error_response


def json_check():
    # Check if request content type is JSON
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.is_json:
            abort(415)
        elif not request.json:
            abort(400, "Empty JSON body")


def ping_url():
    # Get the domain name from the environment variable
    domain_name = current_app.config.get('API_DOMAIN_NAME')
    
    if domain_name:
        url = f"{domain_name}"
        console_log('hostname', f"http://{socket.gethostbyname(socket.gethostname())}:5000")
    else:
        # Otherwise, fall back to using the socket method
        url = f"http://{socket.gethostbyname(socket.gethostname())}:5000"
    
    requests.post('http://http://127.0.0.1:4001/receive-url', json={'url': url})