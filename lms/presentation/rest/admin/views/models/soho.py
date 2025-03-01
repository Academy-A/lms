from lms.adapters.db.models import SohoAccount as SohoAccountDb
from lms.presentation.rest.admin.utils import format_datetime_field
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class SohoAccountModelView(BaseModelView, model=SohoAccountDb):
    category = AdminCategories.MODELS
    column_list = [
        SohoAccountDb.id,
        SohoAccountDb.student,
        SohoAccountDb.email,
        SohoAccountDb.created_at,
        SohoAccountDb.updated_at,
    ]
    column_sortable_list = [
        SohoAccountDb.id,
        SohoAccountDb.email,
        SohoAccountDb.created_at,
        SohoAccountDb.updated_at,
    ]
    column_default_sort = "created_at"
    column_formatters = {
        SohoAccountDb.created_at: format_datetime_field,
        SohoAccountDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [
        SohoAccountDb.email,
        "student.name",
    ]
    column_details_list = [
        SohoAccountDb.id,
        SohoAccountDb.student,
        SohoAccountDb.email,
        SohoAccountDb.created_at,
        SohoAccountDb.updated_at,
    ]
    column_formatters_detail = {
        SohoAccountDb.created_at: format_datetime_field,
        SohoAccountDb.updated_at: format_datetime_field,
    }
    form_include_pk = True
    form_columns = [
        SohoAccountDb.id,
        SohoAccountDb.student,
        SohoAccountDb.email,
    ]
