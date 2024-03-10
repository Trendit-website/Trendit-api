from flask import Flask, request, abort

from ..helpers import check_emerge
from ..helpers.response_helpers import error_response


def json_check():
    # Check if request content type is JSON
    if request.method in ['POST', 'PUT', 'PATCH']:
        if not request.is_json:
            abort(415)
        elif not request.json:
            abort(400, "Empty JSON body")
