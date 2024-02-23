"""empty message

Revision ID: 2022d1d2f309
Revises: 623b9557b241
Create Date: 2024-02-23 11:29:58.527934

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2022d1d2f309"
down_revision: str | None = "623b9557b241"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

teacher_type = postgresql.ENUM("CURATOR", "MENTOR", name="teacher_type")


def upgrade() -> None:
    bind = op.get_bind()
    teacher_type.create(bind)
    op.execute(
        """
        ALTER TABLE offer ALTER COLUMN teacher_type
        TYPE teacher_type USING teacher_type::teacher_type
        """
    )
    op.execute(
        """
        ALTER TABLE student_product ALTER COLUMN teacher_type
        TYPE teacher_type USING teacher_type::teacher_type
        """
    )
    op.execute(
        """
        ALTER TABLE teacher_product ALTER COLUMN type
        TYPE teacher_type USING type::teacher_type
        """
    )


def downgrade() -> None:
    op.alter_column(
        "teacher_product",
        "type",
        existing_type=teacher_type,
        type_=sa.VARCHAR(length=16),
        existing_nullable=False,
    )
    op.alter_column(
        "student_product",
        "teacher_type",
        existing_type=teacher_type,
        type_=sa.VARCHAR(length=16),
        existing_nullable=True,
    )
    op.alter_column(
        "offer",
        "teacher_type",
        existing_type=teacher_type,
        type_=sa.VARCHAR(length=16),
        existing_nullable=True,
    )
    bind = op.get_bind()
    teacher_type.drop(bind)
