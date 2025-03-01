from lms.adapters.db.models import Offer as OfferDb
from lms.presentation.rest.admin.utils import format_datetime_field, format_max_length
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class OfferModelView(BaseModelView, model=OfferDb):
    category = AdminCategories.MODELS
    column_list = [
        OfferDb.id,
        OfferDb.product,
        OfferDb.name,
        OfferDb.cohort,
        OfferDb.teacher_type,
        OfferDb.created_at,
        OfferDb.updated_at,
    ]
    column_sortable_list = [
        OfferDb.id,
        OfferDb.name,
        OfferDb.cohort,
        OfferDb.teacher_type,
    ]
    column_default_sort = "id"
    column_formatters = {
        OfferDb.created_at: format_datetime_field,
        OfferDb.updated_at: format_datetime_field,
        OfferDb.name: format_max_length(40),
    }
    column_searchable_list = [
        OfferDb.id,
        OfferDb.name,
        "product.name",
    ]
    column_details_list = [
        OfferDb.id,
        OfferDb.product,
        OfferDb.name,
        OfferDb.cohort,
        OfferDb.teacher_type,
        OfferDb.created_at,
        OfferDb.updated_at,
    ]
    column_formatters_detail = {
        OfferDb.created_at: format_datetime_field,
        OfferDb.updated_at: format_datetime_field,
    }
    form_include_pk = True
    form_columns = [
        OfferDb.id,
        OfferDb.product,
        OfferDb.name,
        OfferDb.cohort,
        OfferDb.teacher_type,
    ]
