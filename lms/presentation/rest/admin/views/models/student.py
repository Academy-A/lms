from lms.adapters.db.models import Student as StudentDb
from lms.presentation.rest.admin.utils import format_datetime_field, format_vk_id_field
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class StudentModelView(BaseModelView, model=StudentDb):
    category = AdminCategories.MODELS
    column_list = [
        StudentDb.id,
        StudentDb.name,
        StudentDb.vk_id,
        StudentDb.created_at,
        StudentDb.updated_at,
    ]
    column_sortable_list = [
        StudentDb.id,
        StudentDb.name,
        StudentDb.vk_id,
        StudentDb.created_at,
        StudentDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        StudentDb.created_at: format_datetime_field,
        StudentDb.updated_at: format_datetime_field,
        StudentDb.vk_id: format_vk_id_field,
    }
    column_searchable_list = [StudentDb.id, StudentDb.name, StudentDb.vk_id]
    column_details_list = [
        StudentDb.id,
        StudentDb.name,
        StudentDb.vk_id,
        StudentDb.created_at,
        StudentDb.updated_at,
    ]
    column_formatters_detail = {
        StudentDb.created_at: format_datetime_field,
        StudentDb.updated_at: format_datetime_field,
        StudentDb.vk_id: format_vk_id_field,
    }
    form_columns = [
        StudentDb.first_name,
        StudentDb.last_name,
        StudentDb.vk_id,
    ]
