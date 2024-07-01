from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError, SQLAlchemyError )

from ...extensions import db
from ...utils.helpers.telegram_bot import notify_telegram_admins_new_task
from ...utils.helpers.response_helpers import error_response, success_response
from ...models.task import Task, TaskStatus
from ...utils.helpers.basic_helpers import log_exception, console_log


class TasksTelegramController:
    
    @staticmethod
    def get_pending_tasks():
        try:
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get('per_page', 6, type=int)
            
            pagination = Task.query.filter_by(status=TaskStatus.PENDING).paginate(page=page, per_page=per_page, error_out=False)
            
            if page > pagination.pages:
                return success_response('No content', 204, {'tasks': []})
            
            tasks = pagination.items
            
            if not tasks:
                extra_data = {"tasks": []}
                return success_response(f"There are no task orders that are pending approval", 200, extra_data)
            
            for task in  tasks:
                notify_telegram_admins_new_task(task.to_dict())
            
            current_tasks = [task.to_dict() for task in tasks]
            
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "pending_tasks": current_tasks,
            }
            
            
            api_response = success_response('Pending task orders fetched successfully', 200, extra_data)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred fetching social profiles", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response
    
