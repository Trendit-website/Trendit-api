
from app.routes.api_admin import bp
from app.decorators.auth import roles_required
from app.controllers.api_admin.wallet import AdminWalletController

@bp.route('/balance', methods=["GET"])
@roles_required('Admin')
def get_wallet_balance():
    return AdminWalletController.get_wallet_balance()

