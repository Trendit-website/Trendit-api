'''
This module contains Error Handlers for scenarios associated with Trendit³ social tasks.
It helps return proper Error responses on the Trendit³ Flask application.

Author: Emmanuel Olowu
GitHub: https://github.com/zeddyemy
Package: Trendit³
'''

from ..error_handlers import bp
from ..utils.helpers.basic_helpers import log_exception
from ..utils.helpers.response_helpers import error_response
from ..exceptions import PendingTaskError, NoUnassignedTaskError, UniqueSlugError


@bp.app_errorhandler(PendingTaskError)
def handle_pending_task_error(error):
    log_exception('PendingTaskError:', error)
    return error_response(f'{str(error)}', 409)


@bp.app_errorhandler(NoUnassignedTaskError)
def handle_no_unassigned_task_error(error):
    log_exception('NoUnassignedTaskError:', error)
    return error_response(f'{str(error)}', 200)


@bp.app_errorhandler(UniqueSlugError)
def handle_unique_slug_error(error):
    log_exception('UniqueSlugError:', error)
    return error_response(f'{str(error)}', 429)
