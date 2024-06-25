'''
This module contains Error Handlers for slug errors.
It helps return proper Error responses on the Trendit³ Flask application.

Author: Emmanuel Olowu
GitHub: https://github.com/zeddyemy
Package: Trendit³
'''

from ..error_handlers import bp
from ..utils.helpers.basic_helpers import log_exception
from ..utils.helpers.response_helpers import error_response
from ..exceptions import UniqueSlugError


@bp.app_errorhandler(UniqueSlugError)
def handle_unique_slug_error(error):
    log_exception('UniqueSlugError:', error)
    return error_response(f'{str(error)}', 500)
