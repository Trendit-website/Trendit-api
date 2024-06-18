import logging, re
from flask import request, jsonify
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, SQLAlchemyError )
from flask_jwt_extended import get_jwt_identity

from ...extensions import db
from ...utils.helpers.response_helpers import error_response, success_response
from ...models.notification import SocialVerification, SocialVerificationStatus, Notification, MessageType
from ...models.user import Trendit3User, SocialLinks, SocialLinksStatus
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

class SocialVerificationController:

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
                }
            }

            return success_response(msg, 200, extra_data)

        except ValueError as ve:
            logging.error(f"ValueError occurred: {ve}")
            return error_response('Invalid data provided', 400)
        except SQLAlchemyError as sae:
            logging.error(f"Database error occurred: {sae}")
            db.session.rollback()
            return error_response('Database error occurred', 500)
        except Exception as e:
            logging.exception(f"An unexpected error occurred: {e}")
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
                    'x': ['x_verified', 'x_id']
                }

            # Check if social media platform is valid
            if not field_mapping.get(platform):
                return error_response('Invalid social media platform', 400)

            # Initialize social links if absent
            if user.social_links is None:
                kwargs = {key: False for key in field_mapping.values()}
                user.social_links = SocialLinks(**kwargs)
            
            if not is_valid_social_url(link, platform):
                return error_response('Invalid URL for specified platform', 400)
            
            # Set the corresponding social media link
            setattr(user.social_links, field_mapping[platform][1], link)
            setattr(user.social_links, field_mapping[platform][0], SocialLinksStatus.PENDING)

            # Send verification notification
            SocialVerification.send_notification(
                sender_id=sender_id,
                body=link,
                type=platform,
                status=SocialVerificationStatus.PENDING
            )

            # Send a notification to the user that the admin has received their request
            Notification.send_notification(
                sender_id=sender_id,
                body='Your social verification request has been received and is pending approval.',
                recipients=[user] if not isinstance(user, (list, tuple)) else user,
                message_type=MessageType.NOTIFICATION
            )

            # Commit the changes to the database in a single transaction
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

