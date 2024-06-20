import logging, re
from flask import request
from sqlalchemy.exc import ( DataError, DatabaseError, SQLAlchemyError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...utils.helpers.response_helpers import error_response, success_response
from ...models.notification import SocialVerification, SocialVerificationStatus, Notification, MessageType
from ...models.social import SocialLinks, SocialLinkStatus, SocialMediaProfile
from ...models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails
from ...utils.helpers.basic_helpers import log_exception

def is_valid_social_url(url, platform):
    patterns = {
        'facebook': r'https?://(www.facebook.com|facebook.com)/.*',
        'tiktok': r'https?://(www.tiktok.com|tiktok.com)/@.*',
        'instagram': r'https?://(www.instagram.com|instagram.com)/.*',
        'x': r'https?://(www.twitter.com|twitter.com|www.x.com|x.com)/.*'  # Modified pattern for "x"
    }
    pattern = patterns.get(platform)
    if pattern and re.match(pattern, url):
        return True
    return False

class SocialProfileController:
    
    @staticmethod
    def get_social_profiles():
        try:
            user_id = int(get_jwt_identity())

            user = Trendit3User.query.filter_by(id=user_id).first()
            if not user:
                return error_response("User not found", 404)
            
            social_profiles = user.social_media_profiles
            
            if not social_profiles:
                extra_data = {"social_profiles": []}
                return success_response(f"No social media profiles has been submitted", 200, extra_data)
            
            extra_data = {
                "social_profiles": [profile.to_dict() for profile in social_profiles]
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
    def add_social_profile():
        try:
            user_id = int(get_jwt_identity())
            
            user = Trendit3User.query.filter_by(id=user_id).first()
            if not user:
                return error_response("User not found", 404)
            
            data = request.get_json()
            link = data.get('link')
            platform = data.get('platform')
            
            # check user already added a profile for the provided platform
            profile = SocialMediaProfile.query.filter_by(platform=platform, trendit3_user=user)
            if profile:
                return success_response(f"{platform} profile already added", 200)
            
            new_profile = SocialMediaProfile.add_profile(platform=platform, link=link, commit=False, trendit3_user=user)
            
            social_profiles = user.social_media_profiles
            extra_data = {
                "social_profiles": [profile.to_dict() for profile in social_profiles]
            }
            
            # Send verification notification
            SocialVerification.send_notification(
                sender_id=user_id,
                body=link,
                type=platform,
                status=SocialVerificationStatus.PENDING,
                commit=False
            )

            # Send a notification to the user that the admin has received their request
            Notification.send_notification(
                sender_id=user_id,
                body='Your social media verification request has been received and is pending approval.',
                recipients=[user] if not isinstance(user, (list, tuple)) else user,
                message_type=MessageType.NOTIFICATION,
                commit=False
            )
            
            db.session.commit()
            
            api_response = success_response(f"{platform} profile has been submitted for review", 200, extra_data)
            
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred sending verification request", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response
    
    @staticmethod
    def delete_social_profile(platform):
        try:
            user_id = int(get_jwt_identity())

            user = Trendit3User.query.filter_by(id=user_id).first()
            if not user:
                return error_response("User not found", 404)
            
            social_profile = SocialMediaProfile.query.filter_by(platform=platform, trendit3_user_id=user_id)
            
            if not social_profile:
                return error_response(f"No social media profile for {platform}", 404)
            
            social_profile.delete()
            
            api_response = success_response('Social Media account deleted successfully', 200)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred sending verification request", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response



    # DEPRECATED
    @staticmethod
    def get_verified_social_media():
        """Get verified social media for a user"""
        try:
            # data = request.get_json()
            # user_id = data.get('userId')
            user_id = int(get_jwt_identity())
            
            user = Trendit3User.query.filter_by(id=user_id).first()

            msg = "verified social media fetched successfully"

            if not user:
                return error_response('User not found', 404)
            
            social_links = user.social_links

            if not social_links:
                social_links = SocialLinks(trendit3_user_id=user_id)
                db.session.add(social_links)
                db.session.commit()
                social_links = user.social_links
            
            extra_data = {
                'socials': {
                    'facebook_verified': social_links.facebook_verified.value,
                    'facebook_link': social_links.facebook_id,
                    'tiktok_verified': social_links.tiktok_verified.value,
                    'tiktok_link': social_links.tiktok_id,
                    'instagram_verified': social_links.instagram_verified.value,
                    'instagram_link': social_links.instagram_id,
                    'x_verified': social_links.x_verified.value,
                    'x_link': social_links.x_id,
                    'threads_verified': social_links.threads_verified.value,
                    'threads_link': social_links.threads_id
                }
            }

            return success_response(msg, 200, extra_data)

        except ValueError as ve:
            log_exception(f"ValueError occurred: {ve}")
            return error_response('Invalid data provided', 400)
        except SQLAlchemyError as sae:
            db.session.rollback()
            log_exception(f"Database error occurred: {sae}")
            return error_response('Database error occurred', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred: {e}")
            return error_response('Error retrieving verified social media', 500)


    @staticmethod
    def send_social_verification_request():
        try:
            # Receive and parse request data
            data = request.get_json()
            link = data.get('link')
            platform = data.get('type')
            sender_id = int(get_jwt_identity())

            # Fetch the user
            user = Trendit3User.query.filter_by(id=sender_id).first()
            if not user:
                return error_response('User not found', 404)

            # Define field mapping
            field_mapping = {
                    'facebook': ['facebook_verified', 'facebook_id'],
                    'tiktok': ['tiktok_verified', 'tiktok_id'],
                    'instagram': ['instagram_verified', 'instagram_id'],
                    'x': ['x_verified', 'x_id'],
                    'threads': ['threads_verified', 'threads_id'],
                }

            # Check if social media platform is valid
            if not field_mapping.get(platform):
                return error_response('Invalid social media platform', 400)

            # Initialize social links if absent
            if user.social_links is None:
                kwargs = {key: False for key in field_mapping.values()}
                user.social_links = SocialLinks(**kwargs)
            
            # Set the corresponding social media link
            setattr(user.social_links, field_mapping[platform][1], link)
            setattr(user.social_links, field_mapping[platform][0], SocialLinkStatus.PENDING)

            # Send verification notification
            SocialVerification.send_notification(
                sender_id=sender_id,
                body=link,
                type=platform,
                status=SocialVerificationStatus.PENDING,
                commit=False
            )

            # Send a notification to the user that the admin has received their request
            Notification.send_notification(
                sender_id=sender_id,
                body='Your social verification request has been received and is pending approval.',
                recipients=[user] if not isinstance(user, (list, tuple)) else user,
                message_type=MessageType.NOTIFICATION,
                commit=False
            )

            db.session.commit()

            # Return success response
            return success_response('Notification sent successfully', 200)

        except ValueError as ve:
            log_exception(f"ValueError occurred", ve)
            return error_response('Invalid data provided', 400)
        except SQLAlchemyError as sae:
            db.session.rollback()
            log_exception(f"Database error occurred", sae)
            return error_response('Database error occurred', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred sending verification request", e)
            return error_response('An unexpected error. Our developers are already looking into it.', 500)
    
    
    @staticmethod
    def delete_socials(platform):
        try:
            user_id = int(get_jwt_identity())

            # Fetch the user
            user = Trendit3User.query.filter_by(id=user_id).first()
            if not user:
                return error_response('User not found', 404)
            
            
            # Define field mapping
            field_mapping = {
                    'facebook': ['facebook_verified', 'facebook_id'],
                    'tiktok': ['tiktok_verified', 'tiktok_id'],
                    'instagram': ['instagram_verified', 'instagram_id'],
                    'x': ['x_verified', 'x_id'],
                    'threads': ['threads_verified', 'threads_id'],
                }

            # Check if social media platform is valid
            if not field_mapping.get(platform):
                return error_response('Invalid social media platform', 400)

            
            social_links = user.social_links
            
            # Initialize social links if absent
            if social_links is None:
                kwargs = {key: False for key in field_mapping.values()}
                user.social_links = SocialLinks(**kwargs)
                social_links = user.social_links
            
            # Set the corresponding social media link
            setattr(social_links, field_mapping[platform][1], "")
            setattr(social_links, field_mapping[platform][0], SocialLinkStatus.IDLE)
            
            db.session.commit()
            
            api_response = success_response(f"{platform} account removed successfully", 200)

        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error:', e)
            api_response = error_response('Error connecting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An unexpected error occurred deleting a social profile", e)
            api_response = error_response('An unexpected error. Our developers are already looking into it.', 500)
        
        return api_response
    

