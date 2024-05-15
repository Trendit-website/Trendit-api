from app.decorators import roles_required
from app.routes.api_admin import bp
from app.controllers.api_admin import SocialVerificationController

@bp.route('/social_verification_requests', methods=['POST'])
@roles_required('Junior Admin')
def get_social_verification_requests():
    return SocialVerificationController.get_all_social_verification_requests()

@bp.route('/approve_social_verification_request', methods=['POST'])
@roles_required('Junior Admin')
def approve_social_verification_request():
    return SocialVerificationController.approve_social_verification_request()

@bp.route('/reject_social_verification_request', methods=['POST'])
@roles_required('Junior Admin')
def reject_social_verification_request():
    return SocialVerificationController.reject_social_verification_request()