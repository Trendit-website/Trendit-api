import logging
from flask import request
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, SQLAlchemyError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...utils.helpers import log_exception, console_log
from ...utils.helpers.response_helpers import error_response, success_response
from ...utils.helpers.mail_helpers import send_social_profile_status_email
from ...models import SocialLinkStatus, SocialLinks, SocialMediaProfile
from ...models.notification import SocialVerification, SocialVerificationStatus, Notification, NotificationType
from ...models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails


class AdminSocialProfileController:
    
        @staticmethod
        def get_social_profiles():
            try:
                page = request.args.get("page", 1, type=int)
                items_per_page = int("10")
                pagination = SocialMediaProfile.query.order_by(SocialMediaProfile.trendit3_user_id.desc()).paginate(page=page, per_page=items_per_page, error_out=False)
                
                profiles = pagination.items
                current_items = [profile.to_dict() for profile in profiles]
                
                extra_data = {
                    "total": pagination.total,
                    "all_profiles": current_items,
                    "current_page": pagination.page,
                    "total_pages": pagination.pages,
                }
                
                api_response = success_response('Social media profiles fetched successfully', 200, extra_data)
            except (DataError, DatabaseError) as e:
                db.session.rollback()
                log_exception('Database error:', e)
                api_response = error_response('Error connecting to the database.', 500)
            except Exception as e:
                db.session.rollback()
                log_exception(f"An unexpected error occurred fetching social profiles", e)
                api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
            
            return api_response
    
        @staticmethod
        def approve_social_media_profile(profile_id):
            try:
                
                if not profile_id:
                    return error_response("profile_id is missing or empty.", 400)
                
                profile: SocialMediaProfile = SocialMediaProfile.query.filter_by(id=profile_id).first()
                platform: str = profile.platform
                recipient_id: int = profile.trendit3_user_id
                sender: Trendit3User = profile.trendit3_user
                body: str = f"Your {profile.platform.capitalize()} verification request has been approved"
                
                
                # Approve and send notification
                profile.status = SocialLinkStatus.VERIFIED
                
                Notification.add_notification(
                    recipient_id=recipient_id,
                    body=body,
                    notification_type=NotificationType.NOTIFICATION,
                    commit=False
                )

                db.session.commit()
                
                send_social_profile_status_email(sender.email, platform, status=SocialLinkStatus.VERIFIED)
                
                api_response = success_response(f"{sender.full_name}'s {platform} profile  approved successfully", 200)
            except (DataError, DatabaseError) as e:
                db.session.rollback()
                log_exception('Database error occurred approving social profile', e)
                api_response = error_response('Error interacting to the database.', 500)
            except Exception as e:
                db.session.rollback()
                log_exception(f"An unexpected error occurred approving social profiles", e)
                api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
            finally:
                db.session.close()
            
            return api_response
        
        @staticmethod
        def reject_social_media_profile(profile_id):
            try:
                
                if not profile_id:
                    return error_response("profile_id is missing or empty.", 400)
                
                profile: SocialMediaProfile = SocialMediaProfile.query.filter_by(id=profile_id).first()
                platform: str = profile.platform
                recipient_id: int = profile.trendit3_user_id
                sender: Trendit3User = profile.trendit3_user
                body: str = f"Your {profile.platform.capitalize()} verification request has been rejected"
                
                
                # reject and send notification
                profile.status = SocialLinkStatus.REJECTED
                
                Notification.add_notification(
                    recipient_id=recipient_id,
                    body=body,
                    notification_type=NotificationType.NOTIFICATION,
                    commit=False
                )

                db.session.commit()
                
                send_social_profile_status_email(sender.email, platform, status=SocialLinkStatus.REJECTED)
                
                api_response = success_response(f"{sender.full_name}'s {platform} profile rejected successfully", 200)
            except (DataError, DatabaseError) as e:
                db.session.rollback()
                log_exception('Database error occurred rejecting social profile', e)
                api_response = error_response('Error interacting to the database.', 500)
            except Exception as e:
                db.session.rollback()
                log_exception(f"An unexpected error occurred rejecting social profiles", e)
                api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
            finally:
                db.session.close()
            
            return api_response
    
        # DEPRECATED
        @staticmethod
        def get_all_social_verification_requests():
            """Get all social verification requests in the system"""
    
            try:
                page = request.args.get('page', default=1, type=int)
                per_page = request.args.get('per_page', default=20, type=int)
                
                social_verification_requests = SocialVerification.query.order_by(SocialVerification.createdAt.desc()).paginate(page=page, per_page=per_page, error_out=False)
                social_verification_list = [social_verification.to_dict() for social_verification in social_verification_requests.items]
                
                extra_data = {
                    'total': social_verification_requests.total,
                    'pages': social_verification_requests.pages,
                    'current_page': social_verification_requests.page,
                    'social_verification_requests': social_verification_list
                }
    
                return success_response('All social verification requests fetched successfully', 200, extra_data)
            
            except Exception as e:
                logging.exception("An exception occurred trying to get all social verification requests:\n", str(e))
                return error_response('Error getting all social verification requests', 500)
            
    
        @staticmethod
        def approve_social_verification_request():
            """Approve a social verification request"""
            # TODO: change user social id status accordingly [-]
            # TODO: send a notification to the user that their request has been approved [-]
    
            try:
                data = request.get_json()
                user_id = data.get('userId')
                recipient_id = int(get_jwt_identity())
                type = data.get('type')
                link = data.get('link')
                social_verification_id = data.get('socialVerificationId') 
                social_verification = SocialVerification.query.filter_by(id=social_verification_id).first()
                user = Trendit3User.query.filter_by(id=user_id).first()

                body = f'Your {type} verification request has been approved'
                
                if not user:
                    return error_response('User not found', 404)
                
                if not social_verification:
                    return error_response('Social verification request not found', 404)
                
                social_verification.status = SocialVerificationStatus.APPROVED

                # Define field mapping
                field_mapping = {
                    'facebook': ['facebook_verified', 'facebook_id'],
                    'tiktok': ['tiktok_verified', 'tiktok_id'],
                    'instagram': ['instagram_verified', 'instagram_id'],
                    'x': ['x_verified', 'x_id']
                }  

                # Check if social media type is valid
                if not field_mapping.get(type):
                    return error_response('Invalid social media type', 400)

                # Initialize social links if absent
                if user.social_links is None:
                    kwargs = {key: False for key in field_mapping.values()}
                    user.social_links = SocialLinks(**kwargs)
                
                # Set the corresponding social media link
                setattr(user.social_links, field_mapping[type][1], link)
                setattr(user.social_links, field_mapping[type][0], SocialLinkStatus.VERIFIED)
                    
                db.session.commit()
                
                Notification.add_notification(
                    recipient_id=recipient_id,
                    body=body,
                    notification_type=NotificationType.NOTIFICATION
                )

                db.session.close()
                
                return success_response('Social verification request approved successfully', 200)
            
            except ValueError as ve:
                logging.error(f"ValueError occurred: {ve}")
                return error_response('Invalid data provided', 400)
            except SQLAlchemyError as sae:
                logging.error(f"Database error occurred: {sae}")
                db.session.rollback()
                return error_response('Database error occurred', 500)
            except Exception as e:
                logging.exception(f"An unexpected error occurred: {e}")
                db.session.rollback()
                return error_response('Error approving verification request', 500)
            

        @staticmethod
        def reject_social_verification_request():
            """Reject a social verification request"""
            # TODO: change user social id status accordingly [-]
            # TODO: send a notification to the user that their request has been rejected [-]
    
            try:
                data = request.get_json()
                user_id = int(data.get('userId'))
                recipient_id = int(get_jwt_identity())
                type = data.get('type')
                link = data.get('link', '')
                social_verification_id = int(data.get('socialVerificationId'))
                social_verification = SocialVerification.query.filter_by(id=social_verification_id).first()
                user = Trendit3User.query.filter_by(id=user_id).first()

                body = f'Your {type} verification request has been rejected'

                if not user:
                    return error_response('User not found', 404)
                
                if not social_verification:
                    return error_response('Social verification request not found', 404)
                
                social_verification.status = SocialVerificationStatus.REJECTED

                # Define field mapping
                field_mapping = {
                    'facebook': ['facebook_verified', 'facebook_id'],
                    'tiktok': ['tiktok_verified', 'tiktok_id'],
                    'instagram': ['instagram_verified', 'instagram_id'],
                    'x': ['x_verified', 'x_id']
                }

                # Check if social media type is valid
                if not field_mapping.get(type):
                    return error_response('Invalid social media type', 400)

                # Initialize social links if absent
                if user.social_links is None:
                    kwargs = {key: False for key in field_mapping.values()}
                    user.social_links = SocialLinks(**kwargs)
                
                # Set the corresponding social media link
                setattr(user.social_links, field_mapping[type][1], link)
                setattr(user.social_links, field_mapping[type][0], SocialLinkStatus.REJECTED)
                    
                db.session.commit()
                
                Notification.add_notification(
                    recipient_id=recipient_id,
                    body=body,
                    notification_type=NotificationType.NOTIFICATION
                )

                db.session.close()
                
                return success_response('Social verification request rejected successfully', 200)
            
            except ValueError as ve:
                logging.error(f"ValueError occurred: {ve}")
                return error_response('Invalid data provided', 400)
            except SQLAlchemyError as sae:
                logging.error(f"Database error occurred: {sae}")
                db.session.rollback()
                return error_response('Database error occurred', 500)
            except Exception as e:
                logging.exception(f"An unexpected error occurred: {e}")
                db.session.rollback()
                return error_response('Error rejecting verification request', 500)
            
