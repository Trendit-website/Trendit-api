import logging, re
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError, SQLAlchemyError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...utils.helpers.telegram_bot import notify_telegram_admins_new_profile
from ...utils.helpers.response_helpers import error_response, success_response
from ...models.notification import SocialVerification, SocialVerificationStatus, Notification, MessageType
from ...models.social import SocialLinks, SocialLinkStatus, SocialMediaProfile
from ...models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails
from ...utils.helpers.basic_helpers import log_exception, console_log
from ...utils.helpers.user_helpers import get_social_profile


class TelegramController:
    
    @staticmethod
    def get_pending_social_profiles():
        try:
            page = request.args.get("page", 1, type=int)
            per_page = 15
            social_profiles = SocialMediaProfile.query.all()
            
            pagination = SocialMediaProfile.query.filter_by(status=SocialLinkStatus.PENDING) \
                .paginate(page=page, per_page=per_page, error_out=False)
            
            social_profiles = pagination.items
            
            if not social_profiles:
                extra_data = {"social_profiles": []}
                return success_response(f"There are no social profiles pending approval", 200, extra_data)
            
            for profile in social_profiles:
                notify_telegram_admins_new_profile(profile)
            
            current_social_profiles = [profile.to_dict() for profile in social_profiles]
            
            extra_data = {
                'total': pagination.total,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
                "transactions_history": current_social_profiles,
            }
            
            
            api_response = success_response('Pending social media profiles fetched successfully', 200, extra_data)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred fetching social profiles", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response
    
