import logging
from flask import request, jsonify
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError, SQLAlchemyError )
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.utils.helpers.response_helpers import error_response, success_response
from app.models.notification import SocialVerification, SocialVerificationStatus, Notification, MessageType
from app.models.user import Trendit3User, SocialLinks
from ...utils.helpers.mail_helpers import send_other_emails


class SocialVerificationController:

    @staticmethod
    def get_verified_social_media():
        """Get verified social media for a user"""
        try:
            # data = request.get_json()
            # user_id = data.get('userId')
            user_id = int(get_jwt_identity())
            
            user = Trendit3User.query.filter_by(id=user_id).first()

            if not user:
                return error_response('User not found', 404)
            
            social_links = user.social_links

            if not social_links:
                return success_response({
                    'facebook': False,
                    'tiktok': False,
                    'instagram': False,
                    'x': False
                }, 200)
            
            verified_social_media = {
                'facebook': social_links.facebook_verified,
                'tiktok': social_links.tiktok_verified,
                'instagram': social_links.instagram_verified,
                'x': social_links.x_verified
            }

            return success_response(verified_social_media, 200)

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
