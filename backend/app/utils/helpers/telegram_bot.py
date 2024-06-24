import requests

from config import Config
from ...utils.helpers import console_log
from ...models.task import Task, AdvertTask, EngagementTask
from ...models.social import SocialMediaPlatform, SocialMediaProfile



send_msg_url = Config.TELEGRAM_SEND_MSG_URL

def notify_telegram_admins_new_task(task: dict):
    label = f"A New Task Was Just Created"
    
    # get task data
    task_id = task.get("id")
    task_type = task.get("task_type")
    payment_status = task.get("payment_status")
    platform = task.get("platform")
    fee_paid = task.get("fee_paid")
    status = task.get("status")
    date_created = task.get("date_created")

    data = (f"• Task Type: {task_type} \n • Payment Status: {payment_status} \n • Platform: {platform} \n • Amount Paid: {fee_paid} \n • Status: {status} \n • Date Created: {date_created}")
    
    formatted_data = data.join("\n\n Use the Buttons bellow to Approve or Reject")
    
    message = f"\n\n{label:-^12}\n {formatted_data} \n{'//':-^12}\n\n"
    
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
    response = requests.post(send_msg_url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())


def send_profile_notification(profile : SocialMediaProfile):
    label = f"A New Social Media Profile Was Just Submitted:"
    
    profile_id = profile.id
    profile_link = profile.link
    
    message = f"New Social Media Profile Submitted:\nID: {profile_id}\nLink: {profile_link}"
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [[
                {'text': 'Accept', 'callback_data': f'accept_profile_{profile_id}'},
                {'text': 'Reject', 'callback_data': f'reject_profile_{profile_id}'}
            ]]
        }
    }
    response = requests.post(send_msg_url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())