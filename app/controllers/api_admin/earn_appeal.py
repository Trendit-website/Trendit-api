import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.task import TaskPerformance, Task
from app.utils.helpers.response_helpers import error_response, success_response
from app.utils.helpers.basic_helpers import generate_random_string, console_log
from app.models.task import TaskStatus, TaskPaymentStatus
from app.models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails


class EarnAppealController:
    pass