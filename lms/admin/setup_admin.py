import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware import Middleware
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import DropDown
from starlette_admin.contrib.sqla import Admin
from starlette_admin.views import Link

from lms.admin.auth_provider import AuthenticationProvider
from lms.admin.views.models.flow import FlowModelView
from lms.admin.views.models.flow_product import FlowProductModelView
from lms.admin.views.models.offer import OfferModelView
from lms.admin.views.models.product import ProductModelView
from lms.admin.views.models.product_group import ProductGroupModelView
from lms.admin.views.models.reviewer import ReviewerModelView
from lms.admin.views.models.setting import SettingModelView
from lms.admin.views.models.soho import SohoModelView
from lms.admin.views.models.student import StudentModelView
from lms.admin.views.models.student_product import StudentProductModelView
from lms.admin.views.models.subject import SubjectModelView
from lms.admin.views.models.teacher import TeacherModelView
from lms.admin.views.models.teacher_product import TeacherProductModelView
from lms.admin.views.pages.home import HomeView
from lms.db.models import (
    Flow,
    FlowProduct,
    Offer,
    Product,
    ProductGroup,
    Reviewer,
    Setting,
    Soho,
    Student,
    StudentProduct,
    Subject,
    Teacher,
    TeacherProduct,
)

TEMPLATES_DIR = Path(__file__).parent.resolve() / "templates"


def build_admin(
    app: FastAPI, engine: AsyncEngine, project_name: str, secret_key: str
) -> None:
    admin = Admin(
        engine=engine,
        title=project_name,
        templates_dir=os.fspath(TEMPLATES_DIR),
        middlewares=[Middleware(SessionMiddleware, secret_key=secret_key)],
        index_view=HomeView(
            label="Home",
            icon="fa fa-home",
            methods=["GET"],
            add_to_menu=True,
        ),
        auth_provider=AuthenticationProvider(),
    )

    admin.add_view(
        DropDown(
            "Models",
            icon="fa fa-list",
            views=[
                FlowModelView(model=Flow),
                FlowProductModelView(model=FlowProduct),
                OfferModelView(model=Offer),
                ProductGroupModelView(model=ProductGroup),
                ProductModelView(model=Product),
                ReviewerModelView(model=Reviewer),
                SettingModelView(model=Setting),
                SohoModelView(model=Soho),
                StudentModelView(model=Student),
                StudentProductModelView(model=StudentProduct),
                SubjectModelView(model=Subject),
                TeacherModelView(model=Teacher),
                TeacherProductModelView(model=TeacherProduct),
            ],
        )
    )

    # useful links
    admin.add_view(
        Link(
            label="API",
            url="/docs",
            icon="fa fa-laptop",
        )
    )
    admin.add_view(
        Link(
            label="SOHO.LMS",
            url="https://master.soholms.com/",
            icon="fa fa-graduation-cap",
        ),
    )
    admin.mount_to(app)