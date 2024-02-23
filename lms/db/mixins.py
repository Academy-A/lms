from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import (
    Mapped,
    column_property,
    declarative_mixin,
    declared_attr,
    mapped_column,
)


@declarative_mixin
class TimestampMixin:
    @declared_attr
    @classmethod
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, server_default=func.now())

    @declared_attr
    @classmethod
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime,
            server_default=func.now(),
            server_onupdate=func.now(),  # type:ignore[arg-type]
            onupdate=datetime.now,
        )


@declarative_mixin
class DeletableMixin:
    @declared_attr
    @classmethod
    def is_deleted(cls) -> Mapped[bool]:
        return mapped_column(
            Boolean,
            default=False,
            nullable=False,
        )


@declarative_mixin
class NameMixin:
    @declared_attr
    @classmethod
    def first_name(cls) -> Mapped[str]:
        return mapped_column(String(128), nullable=False, default="")

    @declared_attr
    @classmethod
    def last_name(cls) -> Mapped[str]:
        return mapped_column(String(128), nullable=False, default="")

    @declared_attr
    @classmethod
    def name(cls) -> Mapped[str]:
        return column_property(cls.first_name + " " + cls.last_name)

    def __repr__(self) -> str:
        return self.name
