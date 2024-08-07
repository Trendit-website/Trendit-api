from flask import Flask
from threading import Thread
from flask import render_template, current_app
from flask_mail import Message

from app import mail
from config import Config
from ...utils.helpers.basic_helpers import console_log, log_exception
from ...models import Trendit3User, SocialMediaProfile, SocialLinkStatus


def send_async_social_profile_status_email(app: Flask, user_email, platform, status):
    with app.app_context():
        user: Trendit3User = Trendit3User.query.filter(Trendit3User.email == user_email).first()
        social_profile: SocialMediaProfile = SocialMediaProfile.query.filter_by(platform=platform, trendit3_user_id=user.id).first()
        
        console_log("social_profile", social_profile)
        
        subject = "Social Profile Rejected"
        template = render_template(
            "mail/social-rejection.html",
            user=user,
            user_email=user_email,
            social_profile=social_profile
        )
        if status == SocialLinkStatus.VERIFIED:
            subject = "Social Profile Approved"
            template = render_template(
                "mail/social-approval.html",
                user=user,
                user_email=user_email,
                social_profile=social_profile
            )
        
        msg = Message(subject, sender=Config.MAIL_ALIAS, recipients=[user_email], html=template)
        
        try:
            mail.send(msg)
        except Exception as e:
            log_exception(f"EXCEPTION SENDING MAIL FOR {status} SOCIAL PROFILE", e)

def send_social_profile_status_email(user_email, platform, status=SocialLinkStatus.REJECTED) -> None:
    '''
    Asynchronously sends an email about the state of a submitted social profile.

    This function runs in a separate thread and sends an email to the user.

    Args:
        status (str): the status of the social profile (SocialLinkStatus.VERIFIED or SocialLinkStatus.REJECTED)
        user_email (str): The email address of the user.

    Returns:
        None
    '''
    
    Thread(target=send_async_social_profile_status_email, args=(current_app._get_current_object(), user_email, platform, status)).start()
