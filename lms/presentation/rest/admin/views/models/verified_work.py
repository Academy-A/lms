from lms.adapters.db.models import VerifiedWorkFile as VerifiedWorkFileDb
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class VerifiedWorkFileModelView(BaseModelView, model=VerifiedWorkFileDb):
    category = AdminCategories.MODELS
