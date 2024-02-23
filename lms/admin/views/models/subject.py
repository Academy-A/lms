from lms.admin.utils import exlude_property_field, format_datetime_field
from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import Subject as SubjectDb
from lms.generals.models.subject import SubjectProperties

SUBJECT_PROPERTIES_FIELDS = SubjectProperties.model_fields.keys()


class SubjectModelView(BaseModelView, model=SubjectDb):
    category = AdminCategories.MODELS
    column_list = [
        SubjectDb.id,
        SubjectDb.name,
        SubjectDb.created_at,
        SubjectDb.updated_at,
    ]
    column_sortable_list = [
        SubjectDb.id,
        SubjectDb.name,
        SubjectDb.created_at,
        SubjectDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        SubjectDb.created_at: format_datetime_field,
        SubjectDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [SubjectDb.name, SubjectDb.id]
    column_details_list = [
        SubjectDb.id,
        SubjectDb.name,
        SubjectDb.created_at,
        SubjectDb.updated_at,
        *SUBJECT_PROPERTIES_FIELDS,
    ]
    column_formatters_detail = {
        SubjectDb.created_at: format_datetime_field,
        SubjectDb.updated_at: format_datetime_field,
        **{field: exlude_property_field(field) for field in SUBJECT_PROPERTIES_FIELDS},
    }
    form_columns = [
        SubjectDb.name,
        SubjectDb.properties,
    ]
