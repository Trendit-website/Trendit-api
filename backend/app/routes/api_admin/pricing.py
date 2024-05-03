from app.decorators import roles_required
from app.routes.api_admin import bp
from app.controllers.api_admin import PricingController

@bp.route('/pricing', methods=['GET'])
@roles_required('Junior Admin')
def get_all_pricing():
    return PricingController.get_all_pricing()


@bp.route('/add_pricing', methods=['POST'])
@roles_required('Junior Admin')
def add_pricing():
    return PricingController.add_pricing()


@bp.route('/update_pricing', methods=['POST'])
@roles_required('Junior Admin')
def update_pricing():
    return PricingController.update_pricing()


@bp.route('/delete_pricing', methods=['POST'])
@roles_required('Junior Admin')
def delete_pricing():
    return PricingController.delete_pricing()