from lms.admin.utils import format_datetime_field
from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import Reviewer as ReviewerDb


class ReviewerModelView(BaseModelView, model=ReviewerDb):
    category = AdminCategories.MODELS
    column_list = [
        ReviewerDb.id,
        ReviewerDb.name,
        ReviewerDb.subject,
        ReviewerDb.desired,
        ReviewerDb.min_,
        ReviewerDb.max_,
        ReviewerDb.abs_max,
        ReviewerDb.is_active,
        ReviewerDb.created_at,
        ReviewerDb.updated_at,
    ]
    column_sortable_list = [
        ReviewerDb.id,
        ReviewerDb.name,
        ReviewerDb.desired,
        ReviewerDb.min_,
        ReviewerDb.max_,
        ReviewerDb.abs_max,
        ReviewerDb.is_active,
        ReviewerDb.created_at,
        ReviewerDb.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        ReviewerDb.created_at: format_datetime_field,
        ReviewerDb.updated_at: format_datetime_field,
    }
    column_searchable_list = [
        "subject.name",
        ReviewerDb.name,
        ReviewerDb.email,
    ]
    column_details_list = [
        ReviewerDb.id,
        ReviewerDb.name,
        ReviewerDb.email,
        ReviewerDb.subject,
        ReviewerDb.desired,
        ReviewerDb.min_,
        ReviewerDb.max_,
        ReviewerDb.abs_max,
        ReviewerDb.is_active,
        ReviewerDb.created_at,
        ReviewerDb.updated_at,
    ]
    column_formatters_detail = {
        ReviewerDb.created_at: format_datetime_field,
        ReviewerDb.updated_at: format_datetime_field,
    }
    form_columns = [
        ReviewerDb.first_name,
        ReviewerDb.last_name,
        ReviewerDb.email,
        ReviewerDb.subject,
        ReviewerDb.desired,
        ReviewerDb.min_,
        ReviewerDb.max_,
        ReviewerDb.abs_max,
        ReviewerDb.is_active,
    ]
