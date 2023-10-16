from polyfactory import Fixture, Use
from polyfactory.decorators import post_generated
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from src.db.models import Offer, Product, ProductGroup, Soho, Student, Subject
from src.enums import TeacherType

__all__ = [
    "SubjectFactory",
    "ProductGroupFactory",
    "ProductFactory",
    "StudentFactory",
    "SohoFactory",
    "OfferFactory",
    "factories",
]


class SubjectFactory(SQLAlchemyFactory[Subject]):
    __model__ = Subject
    __set_relationships__ = True
    __set_foreign_keys__ = False


class ProductGroupFactory(SQLAlchemyFactory[ProductGroup]):
    __model__ = ProductGroup
    __set_relationships__ = True
    __set_foreign_keys__ = False


class ProductFactory(SQLAlchemyFactory[Product]):
    __model__ = Product
    __set_relationships__ = True
    __set_foreign_keys__ = False

    subject = Fixture(SubjectFactory)
    product_group = Fixture(ProductGroupFactory)


class StudentFactory(SQLAlchemyFactory[Student]):
    __model__ = Student
    __set_relationships__ = True
    __set_foreign_keys__ = False

    @post_generated
    @classmethod
    def fullname(cls, first_name: str, last_name: str) -> str:
        return first_name + " " + last_name


class SohoFactory(SQLAlchemyFactory[Soho]):
    __model__ = Soho
    __set_relationships__ = True
    __set_foreign_keys__ = False

    student = StudentFactory


class OfferFactory(SQLAlchemyFactory[Offer]):
    __model__ = Offer
    __set_relationships__ = True
    __set_foreign_keys__ = False

    teacher_type = Use(SQLAlchemyFactory.__random__.choice, list(TeacherType) + [None])

    product = Fixture(ProductFactory)


factories: list[type[SQLAlchemyFactory]] = [
    SubjectFactory,
    ProductGroupFactory,
    ProductFactory,
    StudentFactory,
    SohoFactory,
    OfferFactory,
]
