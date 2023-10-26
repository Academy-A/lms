import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware import Middleware
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import DropDown
from starlette_admin.contrib.sqla import Admin
from starlette_admin.views import Link

from lms.admin.views.models.soho import SohoModelView
from lms.admin.views.models.student import StudentModelView
from lms.admin.views.pages.home import HomeView
from lms.config import Settings
from lms.db.models import Soho, Student

TEMPLATES_DIR = Path(__file__).parent.resolve() / "templates"


def build_admin(app: FastAPI, settings: Settings, engine: AsyncEngine) -> None:
    admin = Admin(
        engine=engine,
        title=settings.PROJECT_NAME,
        templates_dir=os.fspath(TEMPLATES_DIR),
        middlewares=[Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)],
        index_view=HomeView(
            label="Home",
            icon="fa fa-home",
            methods=["GET"],
            add_to_menu=True,
        ),
    )

    # add pages
    # TODO login page
    # TODO auth provider
    # TODO distribution page
    # TODO change teacher_product for student_produt with expulsion

    # add models
    # TODO student_product
    # TODO teacher
    # TODO reviewer
    # TODO teacher_product
    # TODO product
    # TODO subject
    # TODO
    admin.add_view(
        DropDown(
            "Tables",
            icon="fa fa-list",
            views=[
                StudentModelView(model=Student, icon="fa fa-blog", label="Student"),
                SohoModelView(
                    model=Soho,
                    icon="fa-fa-blog",
                    label="Soho",
                ),
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
