import os
from pathlib import Path

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from lms.admin.auth_provider import AuthBackend
from lms.admin.views.models.distribution import DistributionModelView
from lms.admin.views.models.flow import FlowModelView
from lms.admin.views.models.flow_product import FlowProductModelView
from lms.admin.views.models.offer import OfferModelView
from lms.admin.views.models.product import ProductModelView
from lms.admin.views.models.product_group import ProductGroupModelView
from lms.admin.views.models.reviewer import ReviewerModelView
from lms.admin.views.models.setting import SettingModelView
from lms.admin.views.models.soho import SohoAccountModelView
from lms.admin.views.models.student import StudentModelView
from lms.admin.views.models.student_product import StudentProductModelView
from lms.admin.views.models.subject import SubjectModelView
from lms.admin.views.models.teacher import TeacherModelView
from lms.admin.views.models.teacher_product import TeacherProductModelView
from lms.admin.views.models.verified_work import VerifiedWorkFileModelView
from lms.admin.views.pages.distribution import DistributionView
from lms.admin.views.pages.home import HomePageView
from lms.admin.views.pages.teacher_product_dashboard import TeacherProductDashboardView

TEMPLATES_DIR = Path(__file__).parent.resolve() / "templates"


def configure_admin(
    app: FastAPI,
    session_factory: async_sessionmaker[AsyncSession],
    title: str,
    secret_key: str,
    debug: bool,
) -> None:
    auth_backend = AuthBackend(
        session_factory=session_factory,
        secret_key=secret_key,
    )
    admin = Admin(
        app=app,
        session_maker=session_factory,
        templates_dir=os.fspath(TEMPLATES_DIR),
        debug=debug,
        title=title,
        authentication_backend=auth_backend,
    )
    admin.add_view(HomePageView)
    admin.add_view(DistributionModelView)
    admin.add_view(ProductGroupModelView)
    admin.add_view(ProductModelView)
    admin.add_view(FlowModelView)
    admin.add_view(FlowProductModelView)
    admin.add_view(OfferModelView)
    admin.add_view(ReviewerModelView)
    admin.add_view(SettingModelView)
    admin.add_view(SohoAccountModelView)
    admin.add_view(StudentModelView)
    admin.add_view(StudentProductModelView)
    admin.add_view(SubjectModelView)
    admin.add_view(TeacherModelView)
    admin.add_view(TeacherProductModelView)
    admin.add_view(VerifiedWorkFileModelView)
    admin.add_view(DistributionView)
    admin._views[-1].session_factory = session_factory  # type: ignore[union-attr]
    admin._views[-1].secret_key = secret_key  # type: ignore[union-attr]
    admin.add_view(TeacherProductDashboardView)
    admin._views[-1].session_factory = session_factory  # type: ignore[union-attr]
