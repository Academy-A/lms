from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    case,
    func,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import (
    Mapped,
    column_property,
    mapped_column,
    relationship,
)

from lms.db.base import Base
from lms.db.mixins import NameMixin, TimestampMixin
from lms.db.utils import make_pg_enum
from lms.generals.enums import TeacherType


class Student(TimestampMixin, NameMixin, Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)

    def __repr__(self) -> str:
        return str(self.id) + " " + self.last_name


class SohoAccount(TimestampMixin, Base):
    __tablename__ = "soho"  # type: ignore[assignment]
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    student: Mapped[Student] = relationship("Student")

    def __repr__(self) -> str:
        return f"<Soho id={self.id} email={self.email} student_id={self.email}>"


class Subject(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    properties: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        server_default="{ }",
    )

    def __repr__(self) -> str:
        return self.name


class Flow(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    teacher_products: Mapped[list[TeacherProduct]] = relationship(
        "TeacherProduct", secondary="teacher_product_flow", back_populates="flows"
    )

    def __repr__(self) -> str:
        return str(self.id)


class ProductGroup(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    eng_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    def __repr__(self) -> str:
        return self.name


class Product(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
    name: Mapped[str] = mapped_column(String(1024), index=True, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)

    subject: Mapped[Subject] = relationship("Subject")
    product_group: Mapped[ProductGroup] = relationship("ProductGroup")

    def __repr__(self) -> str:
        return self.name


class FlowProduct(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    flow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("flow.id"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        index=True,
        nullable=False,
    )
    soho_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )

    product: Mapped[Product] = relationship("Product")
    flow: Mapped[Flow] = relationship("Flow")


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
        make_pg_enum(TeacherType, name="teacher_type", schema=None),
        nullable=True,
        default=None,
    )

    product: Mapped[Product] = relationship("Product")

    def __repr__(self) -> str:
        return self.name


class Teacher(TimestampMixin, NameMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)


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

    student_product: Mapped[StudentProduct] = relationship("StudentProduct")
    teacher_product: Mapped[TeacherProduct] = relationship("TeacherProduct")

    def __repr__(self) -> str:
        return (
            f"<TeacherAssignment {self.id} {self.student_product_id} "
            f"{self.teacher_product_id}>"
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
    type: Mapped[TeacherType] = mapped_column(
        make_pg_enum(TeacherType, name="teacher_type", schema=None),
        default=TeacherType.MENTOR.value,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    max_students: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    average_grade: Mapped[float] = mapped_column(Float, default=5, nullable=False)
    grade_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    actual_students: Mapped[int] = column_property(
        select(
            func.count(TeacherAssignment.student_product_id),
        )
        .select_from(TeacherAssignment)
        .where(
            TeacherAssignment.removed_at.is_(None),
            TeacherAssignment.teacher_product_id == id,
        )
        .scalar_subquery()
    )

    fullness: Mapped[float] = column_property(
        case(
            *[
                (
                    max_students > 0,
                    actual_students.expression / max_students,  # type: ignore[attr-defined]
                ),
            ],
            else_=1,
        )
    )

    total_students: Mapped[int] = column_property(
        select(
            func.count(TeacherAssignment.student_product_id),
        )
        .select_from(TeacherAssignment)
        .where(TeacherAssignment.teacher_product_id == id)
        .scalar_subquery(),
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
        .scalar_subquery()
    )

    removability: Mapped[float] = column_property(
        case(
            *[
                (
                    total_students.expression > 0,  # type: ignore[attr-defined]
                    (total_students.expression - removal_students.expression)  # type: ignore[attr-defined]
                    / total_students.expression,  # type: ignore[attr-defined]
                ),
            ],
            else_=1.0,
        ),
    )

    rating_coef: Mapped[float] = column_property(
        case(
            *[
                (
                    average_grade == 0,
                    5 * (1 - fullness.expression) * removability.expression,  # type: ignore[attr-defined]
                ),
            ],
            else_=average_grade * (1 - fullness.expression) * removability.expression,  # type: ignore[attr-defined]
        ),
    )

    teacher: Mapped[Teacher] = relationship("Teacher", lazy="joined")
    product: Mapped[Product] = relationship("Product")
    flows: Mapped[list[Flow]] = relationship(
        "Flow", secondary="teacher_product_flow", back_populates="teacher_products"
    )

    def __repr__(self) -> str:
        return f"{self.teacher.name}, {self.type.value}, " + (
            "active" if self.is_active else "not active"
        )

    @property
    def is_mentor(self) -> bool:
        return self.type == TeacherType.MENTOR

    @property
    def is_curator(self) -> bool:
        return self.type == TeacherType.CURATOR


class StudentProduct(TimestampMixin, Base):
    __table_args__ = (
        CheckConstraint(
            "(teacher_type IS NULL) = (teacher_product_id IS NULL)",
            name="check_teacher",
        ),
        UniqueConstraint("student_id", "product_id"),
    )
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
        make_pg_enum(TeacherType, name="teacher_type", schema=None),
        nullable=True,
        default=None,
    )
    offer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("offer.id"),
        index=True,
        nullable=False,
    )
    flow_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("flow.id"),
        index=True,
        nullable=True,
    )
    cohort: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    teacher_grade: Mapped[int | None] = mapped_column(
        Integer, default=None, nullable=True
    )
    teacher_graded_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=None, nullable=True
    )
    expulsion_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=None,
        index=True,
        nullable=True,
    )

    student: Mapped[Student] = relationship("Student")
    product: Mapped[Product] = relationship("Product")
    teacher_product: Mapped[TeacherProduct | None] = relationship("TeacherProduct")
    offer: Mapped[Offer] = relationship("Offer", lazy="joined")
    flow: Mapped[Flow | None] = relationship("Flow", lazy="joined")


class TeacherProductFlow(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teacher_product.id"),
        nullable=False,
        index=True,
    )
    flow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("flow.id"),
        nullable=False,
        index=True,
    )

    teacher_product: Mapped[TeacherProduct] = relationship("TeacherProduct")
    flow: Mapped[Flow] = relationship("Flow")


class Reviewer(Base, NameMixin, TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subject.id"),
        nullable=False,
        server_default="1",
    )
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    desired: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        server_default="0",
    )
    abs_max: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subject: Mapped[Subject] = relationship("Subject")


class VerifiedWorkFile(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subject.id"), index=True, nullable=False
    )
    student_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("student.id"), index=True, nullable=True
    )
    file_id: Mapped[str] = mapped_column(
        String(128), index=True, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(1024), nullable=False)

    subject: Mapped[Subject] = relationship("Subject")
    student: Mapped[Student | None] = relationship("Student")


class Setting(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        unique=True,
    )
    value: Mapped[str] = mapped_column(String(4096), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")


class User(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(128), nullable=False)


class Distribution(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subject.id"),
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )

    subject: Mapped[Subject] = relationship("Subject")
