from lms.adapters.db.models import FlowProduct as FlowProductDb
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class FlowProductModelView(BaseModelView, model=FlowProductDb):
    category = AdminCategories.MODELS
    column_list = [
        FlowProductDb.id,
        FlowProductDb.flow,
        FlowProductDb.product,
        FlowProductDb.soho_id,
    ]
    column_sortable_list = [
        FlowProductDb.id,
        FlowProductDb.soho_id,
    ]
    column_default_sort = "id"
    column_formatters = {}
    column_searchable_list = [
        "product.name",
        FlowProductDb.flow_id,
        FlowProductDb.soho_id,
    ]
    column_details_list = [
        FlowProductDb.id,
        FlowProductDb.flow,
        FlowProductDb.product,
        FlowProductDb.soho_id,
    ]
    form_columns = [
        FlowProductDb.flow,
        FlowProductDb.product,
        FlowProductDb.soho_id,
    ]
