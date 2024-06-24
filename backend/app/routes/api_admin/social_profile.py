from app.decorators import roles_required
from app.routes.api_admin import bp
from ...controllers.api_admin import AdminSocialProfileController



@bp.route('/social-profiles', methods=["GET"])
@roles_required('Junior Admin')
def get_social_profiles():
    return AdminSocialProfileController.get_social_profiles()

@bp.route('/social-profiles/<profile_id>/approve', methods=['POST'])
@roles_required('Junior Admin')
def approve_social_media_profile(profile_id):
    return AdminSocialProfileController.approve_social_media_profile(profile_id)

@bp.route('/social-profiles/<profile_id>/reject', methods=['POST'])
@roles_required('Junior Admin')
def reject_social_media_profile(profile_id):
    return AdminSocialProfileController.reject_social_media_profile(profile_id)



# DEPRECATED
@bp.route('/social_verification_requests', methods=['POST'])
@roles_required('Junior Admin')
def get_social_verification_requests():
    return AdminSocialProfileController.get_all_social_verification_requests()

@bp.route('/approve_social_verification_request', methods=['POST'])
@roles_required('Junior Admin')
def approve_social_verification_request():
    return AdminSocialProfileController.approve_social_verification_request()

@bp.route('/reject_social_verification_request', methods=['POST'])
@roles_required('Junior Admin')
def reject_social_verification_request():
    return AdminSocialProfileController.reject_social_verification_request()