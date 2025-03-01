from lms.adapters.db.models import TeacherProduct as TeacherProductDb
from lms.presentation.rest.admin.utils import format_datetime_field, format_float_field
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class TeacherProductModelView(BaseModelView, model=TeacherProductDb):
    category = AdminCategories.MODELS
    column_list = [
        TeacherProductDb.id,
        TeacherProductDb.teacher,
        TeacherProductDb.product,
        TeacherProductDb.flows,
        TeacherProductDb.type,
        TeacherProductDb.is_active,
        TeacherProductDb.average_grade,
        TeacherProductDb.actual_students,
        TeacherProductDb.max_students,
        TeacherProductDb.rating_coef,
        TeacherProductDb.created_at,
        TeacherProductDb.updated_at,
    ]
    column_sortable_list = [
        TeacherProductDb.id,
        TeacherProductDb.type,
        TeacherProductDb.is_active,
        TeacherProductDb.max_students,
        TeacherProductDb.average_grade,
        TeacherProductDb.grade_counter,
        TeacherProductDb.actual_students,
        TeacherProductDb.rating_coef,
        TeacherProductDb.created_at,
        TeacherProductDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        TeacherProductDb.created_at: format_datetime_field,
        TeacherProductDb.updated_at: format_datetime_field,
        TeacherProductDb.average_grade: format_float_field(3),
        TeacherProductDb.rating_coef: format_float_field(3),
    }
    column_searchable_list = [
        "product.name",
        "teacher.name",
        TeacherProductDb.type,
    ]
    column_details_list = [
        TeacherProductDb.id,
        TeacherProductDb.product,
        TeacherProductDb.teacher,
        TeacherProductDb.type,
        TeacherProductDb.is_active,
        TeacherProductDb.max_students,
        TeacherProductDb.average_grade,
        TeacherProductDb.grade_counter,
        TeacherProductDb.actual_students,
        TeacherProductDb.rating_coef,
        TeacherProductDb.created_at,
        TeacherProductDb.updated_at,
    ]
    column_formatters_detail = {
        TeacherProductDb.created_at: format_datetime_field,
        TeacherProductDb.updated_at: format_datetime_field,
        TeacherProductDb.average_grade: format_float_field(3),
    }
    form_columns = [
        TeacherProductDb.product,
        TeacherProductDb.teacher,
        TeacherProductDb.type,
        TeacherProductDb.is_active,
        TeacherProductDb.max_students,
        TeacherProductDb.average_grade,
        TeacherProductDb.grade_counter,
        TeacherProductDb.flows,
    ]
