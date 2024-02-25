from lms.admin.utils import format_datetime_field
from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import Flow as FlowDb


class FlowModelView(BaseModelView, model=FlowDb):
    category = AdminCategories.MODELS
    column_list = [
        FlowDb.id,
        FlowDb.created_at,
        FlowDb.updated_at,
    ]
    column_sortable_list = [
        FlowDb.id,
        FlowDb.created_at,
        FlowDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        FlowDb.created_at: format_datetime_field,
        FlowDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [
        FlowDb.id,
    ]
    column_details_list = [
        FlowDb.id,
        FlowDb.created_at,
        FlowDb.updated_at,
    ]
    column_formatters_detail = {
        FlowDb.created_at: format_datetime_field,
        FlowDb.updated_at: format_datetime_field,
    }
    form_include_pk = True
    form_columns = [
        FlowDb.id,
    ]
