from . import bp
from ...controllers.telegram import SocialProfilesTelegramController
from ...decorators import roles_required


@bp.route('/telegram/pending-socials', methods=["GET"])
@roles_required(["Super Admin", "Admin", "Junior Admin"])
def get_pending_social_profiles():
    return SocialProfilesTelegramController.get_pending_social_profiles()

