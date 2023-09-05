from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    case,
    func,
    select,
    text,
)
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from sqlalchemy_utils import ChoiceType

from src.db.base import Base
from src.db.mixins import TimestampMixin


class Student(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")

    products: Mapped[list[Product]] = relationship(
        "Product",
        secondary="student_product",
    )

    soho: Mapped[Soho] = relationship("Soho", back_populates="student", uselist=False)


class Soho(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    student: Mapped[Student] = relationship("Student")


class Subject(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    eng_name: Mapped[str] = mapped_column(String, index=True, unique=True)
    autopilot_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    group_vk_link: Mapped[str] = mapped_column(String(1024), nullable=False)

    products: Mapped[list[Product]] = relationship(
        "Product",
        back_populates="subject",
    )


class ProductGroup(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    eng_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    products: Mapped[list[Product]] = relationship("Product")


class Product(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(1024), index=True, nullable=False)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subject.id"),
        index=True,
        nullable=False,
    )
    product_group_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_group.id"),
        index=True,
        nullable=False,
    )

    subject: Mapped[Subject] = relationship("Subject", back_populates="products")
    product_group: Mapped[ProductGroup] = relationship(
        "ProductGroup",
        back_populates="products",
    )


class TeacherType(enum.StrEnum):
    CURATOR = "CURATOR"
    MENTOR = "MENTOR"


class Offer(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    cohort: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    teacher_type: Mapped[TeacherType | None] = mapped_column(
        ChoiceType(TeacherType, impl=String(16)),
        nullable=True,
        default=None,
    )


class Teacher(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")


class TeacherAssignment(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    student_product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("student_product.id"),
        index=True,
        nullable=False,
    )
    teacher_product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teacher_product.id"),
        index=True,
        nullable=False,
    )
    assignment_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=datetime.now,
    )
    removed_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    def __repr__(self) -> str:
        return (
            f"<TeacherAssignment {self.id} {self.student_product_id} "
            f"{self.teacher_product_id}>"
        )


class StudentProduct(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("student.id"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        index=True,
        nullable=False,
    )
    teacher_product_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("teacher_product.id"),
        index=True,
        nullable=True,
    )
    teacher_type: Mapped[TeacherType | None] = mapped_column(
        ChoiceType(TeacherType, impl=String(16)),
        nullable=True,
        default=None,
    )
    offer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("offer.id"),
        index=True,
        nullable=False,
    )
    cohort: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    teacher_rate: Mapped[int] = mapped_column(Integer, default=None, nullable=True)
    teacher_rate_date: Mapped[date] = mapped_column(Date, default=None, nullable=True)
    expulsion_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=None,
        index=True,
        nullable=True,
    )


class TeacherProduct(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teacher.id"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        index=True,
        nullable=False,
    )
    type: Mapped[TeacherType] = mapped_column(  # noqa: A003
        ChoiceType(TeacherType, impl=String(16)),
        default=TeacherType.MENTOR,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    max_students: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    average_rate: Mapped[int] = mapped_column(Float, default=5, nullable=False)
    rate_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    fullness: Mapped[float] = column_property(
        select(
            func.count(TeacherAssignment.student_product_id),
        )
        .select_from(TeacherAssignment)
        .where(
            TeacherAssignment.removed_at.is_(None),
            TeacherAssignment.teacher_product_id == id,
        )
        .group_by(TeacherAssignment.student_product_id)
        .as_scalar()
        / max_students,
    )

    total_students: Mapped[int] = column_property(
        select(
            func.count(TeacherAssignment.student_product_id),
        )
        .select_from(TeacherAssignment)
        .where(TeacherAssignment.teacher_product_id == id)
        .group_by(TeacherAssignment.student_product_id)
        .as_scalar(),
    )

    removal_students: Mapped[int] = column_property(
        select(
            func.count(TeacherAssignment.student_product_id),
        )
        .select_from(TeacherAssignment)
        .where(
            TeacherAssignment.removed_at.is_not(None),
            TeacherAssignment.teacher_product_id == id,
            TeacherAssignment.removed_at
            > (func.current_timestamp() - text("(interval '1 month')")),
        )
        .group_by(TeacherAssignment.student_product_id)
        .as_scalar(),
    )

    removability: Mapped[float] = column_property(
        case(
            *[
                (
                    total_students.expression > 0,
                    (total_students.expression - removal_students.expression)
                    / total_students.expression,
                ),
            ],
            else_=1.0,
        ),
    )

    rating_coef: Mapped[float] = column_property(
        case(
            *[
                (
                    average_rate == 0,
                    5 * (1 - fullness.expression) * removability.expression,
                ),
            ],
            else_=average_rate * (1 - fullness.expression) * removability.expression,
        ),
    )

    @property
    def is_mentor(self) -> bool:
        return self.type == TeacherType.MENTOR

    @property
    def is_curator(self) -> bool:
        return self.type == TeacherType.CURATOR


class Setting(TimestampMixin, Base):

    """Dynamic config data for app."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        unique=True,
    )
    value: Mapped[str] = mapped_column(String(2048), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
