"""distribution

Revision ID: 3628b0300c0a
Revises: d4c2d6776b30
Create Date: 2024-01-16 04:57:40.412272

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "3628b0300c0a"
down_revision: str | None = "d4c2d6776b30"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "distribution",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("data", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
            name=op.f("fk__distribution__subject_id__subject"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__distribution")),
    )
    op.drop_column("product", "check_spreadsheet_id")
    op.drop_column("product", "drive_folder_id")
    op.add_column(
        "reviewer",
        sa.Column("subject_id", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "reviewer", sa.Column("min_", sa.Integer(), nullable=False, server_default="0")
    )
    op.drop_constraint(
        "fk__reviewer__product_id__product", "reviewer", type_="foreignkey"
    )
    op.drop_constraint(
        "fk__reviewer__teacher_product_id__teacher_product",
        "reviewer",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk__reviewer__subject_id__subject"),
        "reviewer",
        "subject",
        ["subject_id"],
        ["id"],
    )
    op.drop_column("reviewer", "product_id")
    op.drop_column("reviewer", "teacher_product_id")
    op.add_column(
        "subject",
        sa.Column(
            "check_spreadsheet_id",
            sa.String(length=256),
            nullable=False,
            server_default="''",
        ),
    )
    op.add_column(
        "subject",
        sa.Column(
            "drive_folder_id",
            sa.String(length=256),
            nullable=False,
            server_default="''",
        ),
    )


def downgrade() -> None:
    op.drop_column("subject", "drive_folder_id")
    op.drop_column("subject", "check_spreadsheet_id")
    op.add_column(
        "reviewer",
        sa.Column(
            "teacher_product_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "reviewer",
        sa.Column("product_id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(
        op.f("fk__reviewer__subject_id__subject"), "reviewer", type_="foreignkey"
    )
    op.create_foreign_key(
        "fk__reviewer__teacher_product_id__teacher_product",
        "reviewer",
        "teacher_product",
        ["teacher_product_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk__reviewer__product_id__product",
        "reviewer",
        "product",
        ["product_id"],
        ["id"],
    )
    op.drop_column("reviewer", "min_")
    op.drop_column("reviewer", "subject_id")
    op.add_column(
        "product",
        sa.Column(
            "drive_folder_id",
            sa.VARCHAR(length=256),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "product",
        sa.Column(
            "check_spreadsheet_id",
            sa.VARCHAR(length=256),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_table("distribution")
