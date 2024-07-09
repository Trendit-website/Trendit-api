import json
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, )

from .. import api as api_bp
from ....utils.helpers.basic_helpers import log_exception
from ....utils.helpers.response_helpers import error_response

@api_bp.app_errorhandler(json.JSONDecodeError)
def json_decode_error(error):
    return error_response(f"Invalid or no JSON object.", 400)

@api_bp.app_errorhandler(Exception)
def database_Error(error):
    log_exception("SQLalchemy Database Error", error)
    return error_response('An unexpected error. Our developers are already looking into it.', 500)

@api_bp.app_errorhandler(DataError)
def data_error(error):
    log_exception("SQLalchemy Database Error", error)
    return error_response('Error interacting to the database.', 500)

@api_bp.app_errorhandler(DatabaseError)
def database_error(error):
    log_exception("SQLalchemy Database Error", error)
    return error_response('Error interacting to the database.', 500)

