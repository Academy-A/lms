from lms.admin.utils import format_date_field, format_datetime_field
from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import Product as ProductDb


class ProductModelView(BaseModelView, model=ProductDb):
    category = AdminCategories.MODELS
    column_list = [
        ProductDb.id,
        ProductDb.name,
        ProductDb.subject,
        ProductDb.product_group,
        ProductDb.start_date,
        ProductDb.end_date,
        ProductDb.created_at,
        ProductDb.updated_at,
    ]
    column_sortable_list = [
        ProductDb.id,
        ProductDb.name,
        ProductDb.start_date,
        ProductDb.end_date,
        ProductDb.created_at,
        ProductDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        ProductDb.created_at: format_datetime_field,
        ProductDb.updated_at: format_datetime_field,
        ProductDb.start_date: format_date_field,
        ProductDb.end_date: format_date_field,
    }
    column_searchable_list = [
        ProductDb.name,
        "subject.name",
        "product_group.name",
    ]
    column_details_list = [
        ProductDb.id,
        ProductDb.name,
        ProductDb.start_date,
        ProductDb.end_date,
        ProductDb.subject,
        ProductDb.product_group,
        ProductDb.created_at,
        ProductDb.updated_at,
    ]
    column_formatters_detail = {
        ProductDb.created_at: format_datetime_field,
        ProductDb.updated_at: format_datetime_field,
        ProductDb.start_date: format_date_field,
        ProductDb.end_date: format_date_field,
    }
    form_columns = [
        ProductDb.name,
        ProductDb.subject,
        ProductDb.product_group,
        ProductDb.start_date,
        ProductDb.end_date,
    ]
