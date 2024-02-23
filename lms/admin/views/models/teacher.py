from lms.admin.utils import format_datetime_field
from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import Teacher as TeacherDb


class TeacherModelView(BaseModelView, model=TeacherDb):
    category = AdminCategories.MODELS
    column_list = [
        TeacherDb.id,
        TeacherDb.name,
        TeacherDb.vk_id,
        TeacherDb.created_at,
        TeacherDb.updated_at,
    ]
    column_sortable_list = [
        TeacherDb.id,
        TeacherDb.name,
        TeacherDb.vk_id,
        TeacherDb.created_at,
        TeacherDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        TeacherDb.created_at: format_datetime_field,
        TeacherDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [
        TeacherDb.id,
        TeacherDb.name,
        TeacherDb.vk_id,
    ]
    column_details_list = [
        TeacherDb.id,
        TeacherDb.name,
        TeacherDb.vk_id,
        TeacherDb.created_at,
        TeacherDb.updated_at,
    ]
    column_formatters_detail = {
        TeacherDb.created_at: format_datetime_field,
        TeacherDb.updated_at: format_datetime_field,
    }
    form_columns = [
        TeacherDb.first_name,
        TeacherDb.last_name,
        TeacherDb.vk_id,
    ]
