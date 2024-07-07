import requests

from config import Config
from ...utils.helpers import console_log
from ...models.task import Task, AdvertTask, EngagementTask, TaskPerformance
from ...models.social import SocialMediaPlatform, SocialMediaProfile



send_msg_url = Config.TELEGRAM_SEND_MSG_URL

def notify_telegram_admins_new_task(task: Task | AdvertTask | EngagementTask):
    label = f"A New Task Was Just Created"
    
    # get task data
    data = task.to_dict()
    
    task_id = data.get("id")
    task_type = data.get("task_type")
    payment_status = data.get("payment_status")
    platform = data.get("platform")
    fee_paid = data.get("fee_paid")
    status = data.get("status")
    target_country = data.get("target_country")
    target_state = data.get("target_state")
    location = f"{target_state}, {target_country}"
    date_created = data.get("date_created")
    account_link = data.get("account_link")
    
    requested_count = data.get("posts_count", data.get("engagements_count", 0))
    

    count = "No of posts" if data.get("posts_count") else "No of Engagements"
    link = f"• Link: {account_link} \n" if account_link else ""

    data_msg = (
        f"• Task Type: {task_type} \n • Payment Status: {payment_status} \n • Platform: {platform} \n • Amount Paid: {fee_paid} \n • Location: {location} \n • {count}: {requested_count} \n {link} • Status: {status} \n • Date Created: {date_created}"
        )
    
    formatted_data = data_msg
    
    message = f"\n\n{label:-^12}\n\n {formatted_data} \n{'//':-^12}\n\n"
    
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'text': 'Approve', 'callback_data': f'approve_task_{task_id}'},
                    {'text': 'Reject', 'callback_data': f'reject_task_{task_id}'}
                ],
                [
                    {'text': 'View Provided Link', 'url': f'{account_link}'}
                ] if account_link else []
            ]
        }
    }
    response = requests.post(send_msg_url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())

def notify_telegram_admins_new_performed_task(performed_task: TaskPerformance):
    user = performed_task.trendit3_user
    username = user.username
    full_name = f"{user.profile.firstname} {user.profile.lastname}"
    
    performed_task_id = performed_task.id
    performed_task_key = performed_task.key
    task_type = performed_task.task_type
    status = performed_task.status
    task = performed_task.get_task()
    reward_money = performed_task.reward_money
    
    date_started = performed_task.started_at
    date_completed = performed_task.date_completed
    
    label = f"{username} Just performed a task, and is expecting a review:"
    
    data = (f"• Full Name: {full_name} \n • Task ID: {performed_task_id} \n • Task Type: {task_type} \n • Date Started: {date_started} \n • Date Completed: {date_completed} \n • Status: {status} \n\n • Amount to be earned: {reward_money}")
    
    formatted_data = data + f"\n\n "
    
    message = f"\n\n{label:-^12}\n\n {formatted_data} \n{'//':-^12}\n\n"
    
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [[
                {'text': 'Accept', 'callback_data': f'accept_performedTask_{performed_task_id}'},
                {'text': 'Reject', 'callback_data': f'reject_performedTask_{performed_task_id}'}
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
    
    formatted_data = data
    
    message = f"\n\n{label:-^12}\n\n {formatted_data} \n{'//':-^12}\n\n"
    
    payload = {
        'chat_id': Config.TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'text': 'Approve', 'callback_data': f'accept_profile_{profile_id}'},
                    {'text': 'Reject', 'callback_data': f'reject_profile_{profile_id}'}
                ],
                [
                    {'text': 'View Profile', 'url': f'{profile_link}'}
                ]
            ]
        }
    }
    response = requests.post(send_msg_url, json=payload)
    console_log("response", response)
    console_log("response_data", response.json())