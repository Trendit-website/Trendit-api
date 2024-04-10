from flask_jwt_extended import jwt_required

from . import api
from app.controllers.api import ReferralController


@api.route('/referral/generate-link', methods=['GET'])
@jwt_required()
def generate_referral_link():
    return ReferralController.generate_referral_link()


@api.route('referral/history', methods=['GET'])
@jwt_required()
def get_referral_history():
    return ReferralController.get_referral_history()
