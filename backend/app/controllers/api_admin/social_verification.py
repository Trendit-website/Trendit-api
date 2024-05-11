import logging
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.utils.helpers.response_helpers import error_response, success_response
from app.models.notification import SocialVerification, SocialVerificationStatus, Notification, MessageType
from app.models.user import Trendit3User
from ...utils.helpers.mail_helpers import send_other_emails


class SocialVerificationController:
    
        @staticmethod
        def get_all_social_verification_requests():
            """Get all social verification requests in the system"""
    
            try:
                page = request.args.get('page', default=1, type=int)
                per_page = request.args.get('per_page', default=20, type=int)
                
                social_verification_requests = SocialVerification.query.paginate(page=page, per_page=per_page, error_out=False)
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
                sender_id = int(get_jwt_identity())
                type = data.get('type')
                social_verification_id = data.get('socialVerificationId') 
                social_verification = SocialVerification.query.filter_by(id=social_verification_id).first()
                user = Trendit3User.query.filter_by(id=user_id).first()

                body = f'Your {type} verification request has been approved'
                
                if not user:
                    return error_response('User not found', 404)
                
                if not social_verification:
                    return error_response('Social verification request not found', 404)
                
                social_verification.status = SocialVerificationStatus.APPROVED

                if type == 'facebook':
                    user.social_ids.facebook_verified = True

                elif type == 'tiktok':
                    user.social_ids.tiktok_verified = True

                elif type == 'instagram':
                    user.social_ids.instagram_verified = True

                elif type == 'x':
                    user.social_ids.x_verified = True
                    
                db.session.commit()
                
                Notification.send_notification(sender_id=sender_id, recipients=user, body=body, message_type=MessageType.NOTIFICATION)

                db.session.close()
                                
                return success_response('Social verification request approved successfully', 200)
            
            except Exception as e:
                logging.exception("An exception occurred trying to approve social verification request:\n", str(e))
                return error_response('Error approving social verification request', 500)
            

        @staticmethod
        def reject_social_verification_request():
            """Reject a social verification request"""
            # TODO: change user social id status accordingly [-]
            # TODO: send a notification to the user that their request has been rejected [-]
    
            try:
                data = request.get_json()
                user_id = data.get('userId')
                sender_id = int(get_jwt_identity())
                type = data.get('type')
                social_verification_id = data.get('socialVerificationId') 
                social_verification = SocialVerification.query.filter_by(id=social_verification_id).first()
                user = Trendit3User.query.filter_by(id=user_id).first()

                body = f'Your {type} verification request has been rejected'

                if not user:
                    return error_response('User not found', 404)
                
                if not social_verification:
                    return error_response('Social verification request not found', 404)
                
                social_verification.status = SocialVerificationStatus.REJECTED

                if type == 'facebook':
                    user.social_ids.facebook_verified = False

                elif type == 'tiktok':
                    user.social_ids.tiktok_verified = False

                elif type == 'instagram':
                    user.social_ids.instagram_verified = False

                elif type == 'x':
                    user.social_ids.x_verified = False
                    
                db.session.commit()
                
                Notification.send_notification(sender_id=sender_id, recipients=user, body=body, message_type=MessageType.NOTIFICATION)

                db.session.close()
                
                return success_response('Social verification request rejected successfully', 200)
            
            except Exception as e:
                logging.exception("An exception occurred trying to reject social verification request:\n", str(e))
                return error_response('Error rejecting social verification request', 500)