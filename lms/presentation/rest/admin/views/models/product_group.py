from lms.adapters.db.models import ProductGroup as ProductGroupDb
from lms.presentation.rest.admin.utils import format_datetime_field
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class ProductGroupModelView(BaseModelView, model=ProductGroupDb):
    category = AdminCategories.MODELS
    column_list = [
        ProductGroupDb.id,
        ProductGroupDb.name,
        ProductGroupDb.eng_name,
        ProductGroupDb.created_at,
        ProductGroupDb.updated_at,
    ]
    column_sortable_list = [
        ProductGroupDb.id,
        ProductGroupDb.name,
        ProductGroupDb.eng_name,
        ProductGroupDb.created_at,
        ProductGroupDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        ProductGroupDb.created_at: format_datetime_field,
        ProductGroupDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [ProductGroupDb.name, ProductGroupDb.eng_name]
    column_details_list = [
        ProductGroupDb.id,
        ProductGroupDb.name,
        ProductGroupDb.eng_name,
        ProductGroupDb.created_at,
        ProductGroupDb.updated_at,
    ]
    column_formatters_detail = {
        ProductGroupDb.created_at: format_datetime_field,
        ProductGroupDb.updated_at: format_datetime_field,
    }
    form_columns = [
        ProductGroupDb.name,
        ProductGroupDb.eng_name,
    ]
