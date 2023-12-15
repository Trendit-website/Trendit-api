import logging
from flask import request, abort, jsonify, make_response
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import Trendit3User, Profile, ReferralHistory
from app.utils.helpers.basic_helpers import console_log
from app.utils.helpers.user_helpers import generate_referral_code
from app.utils.helpers.response_helpers import *


class ReferralController:
    @staticmethod
    def generate_referral_link():
        error = False
        
        try:
            current_user_id = get_jwt_identity()
            current_user = Trendit3User.query.get(current_user_id)
            current_user_profile = current_user.profile
            
            # generate unique referral code for current user
            referral_code = generate_referral_code(8)
            current_user_profile.update(referral_code=referral_code)
            
            
            referral_link = current_user.to_dict()['referral_link']
            
            msg = 'Referral link generated successfully'
            status_code = 200
            extra_data = {
                'referral_link': referral_link
            }
        except Exception as e:
            error = True
            msg = 'Error generating referral link'
            status_code = 500
            logging.exception("An exception occurred generating referral link:", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)
    
    
    @staticmethod
    def get_referral_history():
        error = False
        
        try:
            page = request.args.get("page", 1, type=int)
            items_per_page = int(10)
            
            current_user_id = get_jwt_identity()
            pagination = ReferralHistory.query.filter_by(trendit3_user_id=current_user_id).order_by(ReferralHistory.date_joined.desc()).paginate(page=page, per_page=items_per_page, error_out=False)
            
            referral_history = pagination.items
            current_referral_history = [rh.to_dict() for rh in referral_history]
            extra_data = {
                "total": pagination.total,
                "referral_history": current_referral_history,
                "current_page": pagination.page,
                "total_pages": pagination.pages,
            }
            
            if not referral_history:
                return success_response('No one has been referred yet', 200, extra_data)
            
            msg = 'Referral history fetched successfully'
            status_code = 200
            
        except Exception as e:
            error = True
            msg = 'Error getting all referral history'
            status_code = 500
            logging.exception("An exception occurred trying to get  referral history:", str(e))
        if error:
            return error_response(msg, status_code)
        else:
            return success_response(msg, status_code, extra_data)