from typing import Any

from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from lms.db.models import (
    Offer,
    Product,
    ProductGroup,
    SohoAccount,
    Student,
    StudentProduct,
    Subject,
    Teacher,
    TeacherAssignment,
    TeacherProduct,
)
from lms.generals.enums import TeacherType
from lms.generals.models.subject import SubjectProperties


class SubjectPropertiesFactory(ModelFactory[SubjectProperties]):
    __model__ = SubjectProperties


def generate_properties() -> dict[str, Any]:
    properties = SubjectPropertiesFactory.build()
    return properties.model_dump(mode="json")


class SubjectFactory(SQLAlchemyFactory[Subject]):
    __model__ = Subject
    __set_relationships__ = False
    __set_foreign_keys__ = False

    properties = generate_properties


class ProductGroupFactory(SQLAlchemyFactory[ProductGroup]):
    __model__ = ProductGroup
    __set_relationships__ = True
    __set_foreign_keys__ = False


class ProductFactory(SQLAlchemyFactory[Product]):
    __model__ = Product
    __set_relationships__ = True
    __set_foreign_keys__ = False

    subject = SubjectFactory
    product_group = ProductGroupFactory
    reviewers = []


class StudentFactory(SQLAlchemyFactory[Student]):
    __model__ = Student
    __set_relationships__ = True
    __set_foreign_keys__ = False


class SohoAccountFactory(SQLAlchemyFactory[SohoAccount]):
    __model__ = SohoAccount
    __set_relationships__ = True
    __set_foreign_keys__ = False

    student = StudentFactory


class OfferFactory(SQLAlchemyFactory[Offer]):
    __model__ = Offer
    __set_relationships__ = True
    __set_foreign_keys__ = False

    teacher_type = Use(SQLAlchemyFactory.__random__.choice, list(TeacherType))

    product = ProductFactory


class TeacherFactory(SQLAlchemyFactory[Teacher]):
    __model__ = Teacher
    __set_relationships__ = True
    __set_foreign_keys__ = False


class TeacherProductFactory(SQLAlchemyFactory[TeacherProduct]):
    __model__ = TeacherProduct
    __set_relationships__ = True
    __set_foreign_keys__ = False

    type = Use(SQLAlchemyFactory.__random__.choice, list(TeacherType))

    teacher = TeacherFactory
    product = ProductFactory


class StudentProductFactory(SQLAlchemyFactory[StudentProduct]):
    __model__ = StudentProduct
    __set_relationships__ = True
    __set_foreign_keys__ = False

    teacher_type = None

    student = StudentFactory
    product = ProductFactory
    offer = OfferFactory
    teacher_product = TeacherProductFactory


class TeacherAssignmentFactory(SQLAlchemyFactory[TeacherAssignment]):
    __model__ = TeacherAssignment
    __set_relationships__ = True
    __set_foreign_keys__ = False

    student_product = StudentProductFactory
    teacher_product = TeacherProductFactory


factories: list[type[SQLAlchemyFactory]] = [
    OfferFactory,
    ProductFactory,
    ProductGroupFactory,
    SohoAccountFactory,
    StudentFactory,
    StudentProductFactory,
    SubjectFactory,
    TeacherAssignmentFactory,
    TeacherFactory,
    TeacherProductFactory,
]
