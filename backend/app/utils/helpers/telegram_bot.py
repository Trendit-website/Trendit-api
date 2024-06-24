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
    target_country = task.get("target_country")
    target_state = task.get("target_state")
    location = f"{target_state}, {target_country}"
    date_created = task.get("date_created")

    data = (f"• Task Type: {task_type} \n • Payment Status: {payment_status} \n • Platform: {platform} \n • Amount Paid: {fee_paid} \n • Status: {status} \n • Location: {location} \n • Date Created: {date_created}")
    
    formatted_data = data + f"\n\n Use the Buttons bellow to Approve or Reject"
    
    message = f"\n\n{label:-^12}\n\n {formatted_data} \n{'//':-^12}\n\n"
    
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [[
                {'text': 'Approve', 'callback_data': f'approve_task_{task_id}'},
                {'text': 'Reject', 'callback_data': f'reject_task_{task_id}'}
            ]]
        }
    }
    response = requests.post(send_msg_url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())


def notify_telegram_admins_new_profile(social_profile : SocialMediaProfile):
    user = social_profile.trendit3_user
    username = user.username
    full_name = f"{user.profile.firstname} {user.profile.lastname}"
    
    profile_id = social_profile.id
    profile_link = social_profile.link
    platform = social_profile.platform
    status = social_profile.status.value
    
    label = f"{username} Just submitted a New Social Media Profile for review:"
    
    data = (f"• Full Name: {full_name} \n • Profile ID: {profile_id} \n • Platform: {platform} \n • Profile Link: {profile_link} \n • Status: {status}")
    
    formatted_data = data + f"\n\n Use the Buttons bellow to Approve or Reject"
    
    message = f"\n\n{label:-^12}\n\n {formatted_data} \n{'//':-^12}\n\n"
    
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [[
                {'text': 'Approve', 'callback_data': f'accept_profile_{profile_id}'},
                {'text': 'Reject', 'callback_data': f'reject_profile_{profile_id}'}
            ]]
        }
    }
    response = requests.post(send_msg_url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())