from lms.admin.utils import format_datetime_field
from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import Setting as SettingDb


class SettingModelView(BaseModelView, model=SettingDb):
    category = AdminCategories.MODELS
    column_list = [
        SettingDb.id,
        SettingDb.key,
        SettingDb.description,
        SettingDb.created_at,
        SettingDb.updated_at,
    ]
    column_sortable_list = [
        SettingDb.id,
        SettingDb.key,
        SettingDb.description,
        SettingDb.created_at,
        SettingDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        SettingDb.created_at: format_datetime_field,
        SettingDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [SettingDb.key, SettingDb.description]
    column_details_list = [
        SettingDb.id,
        SettingDb.key,
        SettingDb.value,
        SettingDb.description,
        SettingDb.created_at,
        SettingDb.updated_at,
    ]
    column_formatters_detail = {
        SettingDb.created_at: format_datetime_field,
        SettingDb.updated_at: format_datetime_field,
    }
    form_columns = [
        SettingDb.key,
        SettingDb.value,
        SettingDb.description,
    ]
