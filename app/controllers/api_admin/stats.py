import requests
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError )
from datetime import datetime, date, timedelta
from sqlalchemy import func


from ...extensions import db
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.basic_helpers import log_exception, console_log
from ...utils.payments.flutterwave import flutterwave_fetch_balance

from ...models import Trendit3User, Task, TaskStatus


class AdminStatsController:

    @staticmethod
    def get_statistics():
        try:
            period = request.args.get('period', 'day')  # Default to 'day'
            
            today = date.today()
            
            if period == 'day':
                start_date = today
                end_date = today + timedelta(days=1)
            elif period == 'month':
                start_date = today.replace(day=1)
                end_date = (start_date + timedelta(days=32)).replace(day=1)
            elif period == 'year':
                start_date = today.replace(month=1, day=1)
                end_date = start_date.replace(year=start_date.year + 1)
            else:
                return error_response("Invalid period specified", 400)
            
            
            new_signups = db.session.query(func.count(Trendit3User.id)).filter(Trendit3User.date_joined >= start_date, Trendit3User.date_joined < end_date).scalar()
            new_task = db.session.query(func.count(Task.id)).filter(Task.date_created >= start_date, Task.date_created < end_date).scalar()
            
            approved_tasks = db.session.query(func.count(Task.id)).filter(Task.date_created >= start_date, Task.date_created < end_date, Task.status==TaskStatus.APPROVED).scalar()
            declined_tasks = db.session.query(func.count(Task.id)).filter(Task.date_created >= start_date, Task.date_created < end_date, Task.status==TaskStatus.DECLINED).scalar()
            
            
            
            extra_data={
                "stats": {
                    "new_signups": new_signups,
                    "new_task": new_task,
                    "approved_tasks": approved_tasks,
                    "declined_tasks": declined_tasks
                }
            }
            
            api_response = success_response("statistics fetched successfully", 200, extra_data)
        except requests.exceptions.RequestException as e:
            log_exception("A RequestException occurred fetching statistics", e)
            api_response = error_response("Error fetching statistics", 500)
        except (DataError, DatabaseError) as e:
            log_exception(f"An exception occurred during database operation:", e)
            api_response = error_response("Database error occurred", 500)
        except Exception as e:
            log_exception(f"An unexpected exception occurred fetching statistics", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response

