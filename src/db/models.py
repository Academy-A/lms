from __future__ import annotations

from datetime import date, datetime

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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ChoiceType

from src.db.base import Base
from src.db.mixins import TimestampMixin
from src.enums import TeacherType


class Student(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")

    def __repr__(self) -> str:
        return (
            f"<Student id={self.id} vk_id={self.vk_id} "
            f"first_name={self.first_name} last_name={self.last_name}>"
        )


class Soho(TimestampMixin, Base):
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
    eng_name: Mapped[str] = mapped_column(String, index=True, unique=True)
    autopilot_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    group_vk_url: Mapped[str] = mapped_column(String(1024), nullable=False)


class Flow(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f"<Flow id={self.id}>"


class ProductGroup(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    eng_name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)


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
    check_spreadsheet_id: Mapped[str] = mapped_column(String(256), nullable=False)
    drive_folder_id: Mapped[str] = mapped_column(String(256), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, index=True, nullable=True)
    end_date: Mapped[date] = mapped_column(Date, index=True, nullable=True)

    subject: Mapped[Subject] = relationship("Subject")
    product_group: Mapped[ProductGroup] = relationship("ProductGroup")


class FlowProduct(Base):
    flow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flow.id"), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product.id"), primary_key=True
    )
    soho_id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)

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
        ChoiceType(TeacherType, impl=String(16)),
        nullable=True,
        default=None,
    )

    product: Mapped[Product] = relationship("Product")

    @property
    def is_alone(self) -> bool:
        return self.teacher_type is None


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

    student_product: Mapped[StudentProduct] = relationship("StudentProduct")
    teacher_product: Mapped[TeacherProduct] = relationship("TeacherProduct")

    def __repr__(self) -> str:
        return (
            f"<TeacherAssignment {self.id} {self.student_product_id} "
            f"{self.teacher_product_id}>"
        )


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
    offer: Mapped[Offer] = relationship("Offer")
    flow: Mapped[Flow | None] = relationship("Flow")


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
    average_grade: Mapped[int] = mapped_column(Float, default=5, nullable=False)
    grade_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # fullness: Mapped[float] = column_property(
    #     select(
    #         func.count(TeacherAssignment.student_product_id),
    #     )
    #     .select_from(TeacherAssignment)
    #     .where(
    #         TeacherAssignment.removed_at.is_(None),
    #         TeacherAssignment.teacher_product_id == id,
    #     )
    #     .scalar_subquery()
    #     / max_students,
    # )

    # total_students: Mapped[int] = column_property(
    #     select(
    #         func.count(TeacherAssignment.student_product_id),
    #     )
    #     .select_from(TeacherAssignment)
    #     .where(TeacherAssignment.teacher_product_id == id)
    #     .scalar_subquery(),
    # )

    # removal_students: Mapped[int] = column_property(
    #     select(
    #         func.count(TeacherAssignment.student_product_id),
    #     )
    #     .select_from(TeacherAssignment)
    #     .where(
    #         TeacherAssignment.removed_at.is_not(None),
    #         TeacherAssignment.teacher_product_id == id,
    #         TeacherAssignment.removed_at
    #         > (func.current_timestamp() - text("(interval '1 month')")),
    #     )
    #     .scalar_subquery(),
    # )

    # removability: Mapped[float] = column_property(
    #     case(
    #         *[
    #             (
    #                 total_students.expression > 0,  # type: ignore[attr-defined]
    #                 (total_students.expression - removal_students.expression)  # type: ignore[attr-defined]
    #                 / total_students.expression,  # type: ignore[attr-defined]
    #             ),
    #         ],
    #         else_=1.0,
    #     ),
    # )

    # rating_coef: Mapped[float] = column_property(
    #     case(
    #         *[
    #             (
    #                 average_grade == 0,
    #                 5 * (1 - fullness.expression) * removability.expression,  # type: ignore[attr-defined]
    #             ),
    #         ],
    #         else_=average_grade * (1 - fullness.expression) * removability.expression,  # type: ignore[attr-defined]
    #     ),
    # )

    teacher: Mapped[Teacher] = relationship("Teacher")
    product: Mapped[Product] = relationship("Product")

    @property
    def is_mentor(self) -> bool:
        return self.type == TeacherType.MENTOR

    @property
    def is_curator(self) -> bool:
        return self.type == TeacherType.CURATOR


class TeacherProductFlow(Base):
    teacher_product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teacher_product.id"), primary_key=True
    )
    flow_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("flow.id"), primary_key=True
    )

    teacher_product: Mapped[TeacherProduct] = relationship("TeacherProduct")
    flow: Mapped[Flow] = relationship("Flow")


class Reviewer(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    last_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id"),
        nullable=False,
    )
    teacher_product_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("teacher_product.id"),
        nullable=True,
    )
    email: Mapped[str] = mapped_column(String(128), nullable=False)
    desired: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    abs_max: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product: Mapped[Product] = relationship("Product")
    teacher_product: Mapped[TeacherProduct | None] = relationship("TeacherProduct")


class VerifiedWorkFile(TimestampMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subject.id"), index=True, nullable=False
    )
    student_id: Mapped[int] = mapped_column(
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
