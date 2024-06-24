import requests

from config import Config
from ...utils.helpers import console_log
from ...models.task import Task, AdvertTask, EngagementTask
from ...models.social import SocialMediaPlatform




def notify_telegram_admins_new_task(task: dict):
    label = f"New Task Created"
    
    task_id = task.id
    
    data = (f"• Task Type: {task.get("task_type")} \n • Payment Status: {task.get("payment_status")} \n • Platform: {task.get("platform")} \n • Amount Paid: {task.get("fee_paid")} \n • Status: {task.get("status")} \n • Date Created: {task.get("date_created")}")
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    message = f"\n\n{label:-^6}\n {data} \n{'//':-^6}\n\n"
    
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [[
                {'text': 'Approve', 'callback_data': f'approve_{task_id}'},
                {'text': 'Reject', 'callback_data': f'reject_{task_id}'}
            ]]
        }
    }
    response = requests.post(url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())

