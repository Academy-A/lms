from lms.admin.views.base import AdminCategories, BaseModelView
from lms.db.models import VerifiedWorkFile as VerifiedWorkFileDb


class VerifiedWorkFileModelView(BaseModelView, model=VerifiedWorkFileDb):
    category = AdminCategories.MODELS
