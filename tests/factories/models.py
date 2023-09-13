import factory
import factory.fuzzy

from src.db.models import (
    Offer,
    Soho,
    Student,
    Subject,
    ProductGroup,
    Product,
    TeacherType,
)
from tests.factories.base import AsyncFactory

__all__ = [
    "SubjectFactory",
    "ProductGroupFactory",
    "ProductFactory",
    "StudentFactory",
    "SohoFactory",
    "OfferFactory",
    "factories",
]


class SubjectFactory(AsyncFactory):
    class Meta:
        model = Subject

    id = factory.Sequence(lambda n: n)
    name = factory.fuzzy.FuzzyText(length=12)
    eng_name = factory.fuzzy.FuzzyText(length=5)
    autopilot_url = factory.Faker("url")
    group_vk_url = factory.Faker("url")


class ProductGroupFactory(AsyncFactory):
    class Meta:
        model = ProductGroup

    id = factory.Sequence(lambda n: n)
    name = factory.fuzzy.FuzzyText(length=256)
    eng_name = factory.fuzzy.FuzzyText(length=256)


class ProductFactory(AsyncFactory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.fuzzy.FuzzyText(length=256)

    subject = factory.SubFactory(SubjectFactory)
    product_group = factory.SubFactory(ProductGroupFactory)


class StudentFactory(AsyncFactory):
    class Meta:
        model = Student

    id = factory.Sequence(lambda n: n)
    vk_id = factory.Sequence(lambda n: n)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class SohoFactory(AsyncFactory):
    class Meta:
        model = Soho

    id = factory.Sequence(lambda n: n)
    email = factory.Faker("ascii_free_email")

    student = factory.SubFactory(StudentFactory)


class OfferFactory(AsyncFactory):
    class Meta:
        model = Offer

    id = factory.Sequence(lambda n: n)
    name = factory.fuzzy.FuzzyText(length=128)
    cohort = factory.fuzzy.FuzzyInteger(0, 10)
    teacher_type = factory.fuzzy.FuzzyChoice(TeacherType)

    product = factory.SubFactory(ProductFactory)


factories: list[type[AsyncFactory]] = [
    SubjectFactory,
    ProductGroupFactory,
    ProductFactory,
    StudentFactory,
    SohoFactory,
    OfferFactory,
]
