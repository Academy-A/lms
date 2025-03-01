from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2022d1d2f309"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "flow",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__flow")),
    )
    op.create_table(
        "product_group",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("eng_name", sa.String(length=256), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__product_group")),
    )
    op.create_index(
        op.f("ix__product_group__eng_name"), "product_group", ["eng_name"], unique=False
    )
    op.create_index(
        op.f("ix__product_group__name"), "product_group", ["name"], unique=False
    )
    op.create_table(
        "setting",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.String(length=4096), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__setting")),
    )
    op.create_index(op.f("ix__setting__key"), "setting", ["key"], unique=True)
    op.create_table(
        "student",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("vk_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__student")),
        sa.UniqueConstraint("vk_id", name=op.f("uq__student__vk_id")),
    )
    op.create_table(
        "subject",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "properties",
            postgresql.JSON(astext_type=sa.Text()),
            server_default="{ }",
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__subject")),
    )
    op.create_index(op.f("ix__subject__name"), "subject", ["name"], unique=False)
    op.create_table(
        "teacher",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vk_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__teacher")),
    )
    op.create_index(op.f("ix__teacher__vk_id"), "teacher", ["vk_id"], unique=True)
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__user")),
    )
    op.create_index(op.f("ix__user__username"), "user", ["username"], unique=True)
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
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("product_group_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=1024), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["product_group_id"],
            ["product_group.id"],
            name=op.f("fk__product__product_group_id__product_group"),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
            name=op.f("fk__product__subject_id__subject"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__product")),
    )
    op.create_index(
        op.f("ix__product__end_date"), "product", ["end_date"], unique=False
    )
    op.create_index(op.f("ix__product__name"), "product", ["name"], unique=False)
    op.create_index(
        op.f("ix__product__product_group_id"),
        "product",
        ["product_group_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__product__start_date"), "product", ["start_date"], unique=False
    )
    op.create_index(
        op.f("ix__product__subject_id"), "product", ["subject_id"], unique=False
    )
    op.create_table(
        "reviewer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), server_default="1", nullable=False),
        sa.Column("email", sa.String(length=128), nullable=False),
        sa.Column("desired", sa.Integer(), nullable=False),
        sa.Column("max_", sa.Integer(), nullable=False),
        sa.Column("min_", sa.Integer(), server_default="0", nullable=False),
        sa.Column("abs_max", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
            name=op.f("fk__reviewer__subject_id__subject"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__reviewer")),
    )
    op.create_table(
        "soho",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("email", sa.String(length=128), nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["student.id"],
            name=op.f("fk__soho__student_id__student"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__soho")),
        sa.UniqueConstraint("student_id", name=op.f("uq__soho__student_id")),
    )
    op.create_table(
        "verified_work_file",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column("file_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["student.id"],
            name=op.f("fk__verified_work_file__student_id__student"),
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subject.id"],
            name=op.f("fk__verified_work_file__subject_id__subject"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__verified_work_file")),
    )
    op.create_index(
        op.f("ix__verified_work_file__file_id"),
        "verified_work_file",
        ["file_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix__verified_work_file__student_id"),
        "verified_work_file",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__verified_work_file__subject_id"),
        "verified_work_file",
        ["subject_id"],
        unique=False,
    )
    op.create_table(
        "flow_product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("flow_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("soho_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["flow_id"], ["flow.id"], name=op.f("fk__flow_product__flow_id__flow")
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            name=op.f("fk__flow_product__product_id__product"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__flow_product")),
    )
    op.create_index(
        op.f("ix__flow_product__flow_id"), "flow_product", ["flow_id"], unique=False
    )
    op.create_index(
        op.f("ix__flow_product__product_id"),
        "flow_product",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__flow_product__soho_id"), "flow_product", ["soho_id"], unique=True
    )
    op.create_table(
        "offer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=2048), nullable=False),
        sa.Column("cohort", sa.Integer(), nullable=False),
        sa.Column(
            "teacher_type",
            postgresql.ENUM("CURATOR", "MENTOR", name="teacher_type"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["product.id"], name=op.f("fk__offer__product_id__product")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__offer")),
        sa.UniqueConstraint("name", name=op.f("uq__offer__name")),
    )
    op.create_index(op.f("ix__offer__cohort"), "offer", ["cohort"], unique=False)
    op.create_index(
        op.f("ix__offer__product_id"), "offer", ["product_id"], unique=False
    )
    op.create_table(
        "teacher_product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM("CURATOR", "MENTOR", name="teacher_type"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("max_students", sa.Integer(), nullable=False),
        sa.Column("average_grade", sa.Float(), nullable=False),
        sa.Column("grade_counter", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            name=op.f("fk__teacher_product__product_id__product"),
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["teacher.id"],
            name=op.f("fk__teacher_product__teacher_id__teacher"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__teacher_product")),
    )
    op.create_index(
        op.f("ix__teacher_product__product_id"),
        "teacher_product",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__teacher_product__teacher_id"),
        "teacher_product",
        ["teacher_id"],
        unique=False,
    )
    op.create_table(
        "student_product",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("teacher_product_id", sa.Integer(), nullable=True),
        sa.Column(
            "teacher_type",
            postgresql.ENUM("CURATOR", "MENTOR", name="teacher_type"),
            nullable=True,
        ),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("flow_id", sa.Integer(), nullable=True),
        sa.Column("cohort", sa.Integer(), nullable=False),
        sa.Column("teacher_grade", sa.Integer(), nullable=True),
        sa.Column("teacher_graded_at", sa.DateTime(), nullable=True),
        sa.Column("expulsion_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.CheckConstraint(
            "(teacher_type IS NULL) = (teacher_product_id IS NULL)",
            name=op.f("ck__student_product__check_teacher"),
        ),
        sa.ForeignKeyConstraint(
            ["flow_id"], ["flow.id"], name=op.f("fk__student_product__flow_id__flow")
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offer.id"],
            name=op.f("fk__student_product__offer_id__offer"),
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            name=op.f("fk__student_product__product_id__product"),
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["student.id"],
            name=op.f("fk__student_product__student_id__student"),
        ),
        sa.ForeignKeyConstraint(
            ["teacher_product_id"],
            ["teacher_product.id"],
            name=op.f("fk__student_product__teacher_product_id__teacher_product"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__student_product")),
        sa.UniqueConstraint(
            "student_id",
            "product_id",
            name=op.f("uq__student_product__student_id_product_id"),
        ),
    )
    op.create_index(
        op.f("ix__student_product__cohort"), "student_product", ["cohort"], unique=False
    )
    op.create_index(
        op.f("ix__student_product__expulsion_at"),
        "student_product",
        ["expulsion_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix__student_product__flow_id"),
        "student_product",
        ["flow_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__student_product__offer_id"),
        "student_product",
        ["offer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__student_product__product_id"),
        "student_product",
        ["product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__student_product__student_id"),
        "student_product",
        ["student_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__student_product__teacher_product_id"),
        "student_product",
        ["teacher_product_id"],
        unique=False,
    )
    op.create_table(
        "teacher_product_flow",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("teacher_product_id", sa.Integer(), nullable=False),
        sa.Column("flow_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["flow_id"],
            ["flow.id"],
            name=op.f("fk__teacher_product_flow__flow_id__flow"),
        ),
        sa.ForeignKeyConstraint(
            ["teacher_product_id"],
            ["teacher_product.id"],
            name=op.f("fk__teacher_product_flow__teacher_product_id__teacher_product"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__teacher_product_flow")),
    )
    op.create_index(
        op.f("ix__teacher_product_flow__flow_id"),
        "teacher_product_flow",
        ["flow_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__teacher_product_flow__teacher_product_id"),
        "teacher_product_flow",
        ["teacher_product_id"],
        unique=False,
    )
    op.create_table(
        "teacher_assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_product_id", sa.Integer(), nullable=False),
        sa.Column("teacher_product_id", sa.Integer(), nullable=False),
        sa.Column("assignment_at", sa.DateTime(), nullable=False),
        sa.Column("removed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["student_product_id"],
            ["student_product.id"],
            name=op.f("fk__teacher_assignment__student_product_id__student_product"),
        ),
        sa.ForeignKeyConstraint(
            ["teacher_product_id"],
            ["teacher_product.id"],
            name=op.f("fk__teacher_assignment__teacher_product_id__teacher_product"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__teacher_assignment")),
    )
    op.create_index(
        op.f("ix__teacher_assignment__student_product_id"),
        "teacher_assignment",
        ["student_product_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix__teacher_assignment__teacher_product_id"),
        "teacher_assignment",
        ["teacher_product_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix__teacher_assignment__teacher_product_id"),
        table_name="teacher_assignment",
    )
    op.drop_index(
        op.f("ix__teacher_assignment__student_product_id"),
        table_name="teacher_assignment",
    )
    op.drop_table("teacher_assignment")
    op.drop_index(
        op.f("ix__teacher_product_flow__teacher_product_id"),
        table_name="teacher_product_flow",
    )
    op.drop_index(
        op.f("ix__teacher_product_flow__flow_id"), table_name="teacher_product_flow"
    )
    op.drop_table("teacher_product_flow")
    op.drop_index(
        op.f("ix__student_product__teacher_product_id"), table_name="student_product"
    )
    op.drop_index(op.f("ix__student_product__student_id"), table_name="student_product")
    op.drop_index(op.f("ix__student_product__product_id"), table_name="student_product")
    op.drop_index(op.f("ix__student_product__offer_id"), table_name="student_product")
    op.drop_index(op.f("ix__student_product__flow_id"), table_name="student_product")
    op.drop_index(
        op.f("ix__student_product__expulsion_at"), table_name="student_product"
    )
    op.drop_index(op.f("ix__student_product__cohort"), table_name="student_product")
    op.drop_table("student_product")
    op.drop_index(op.f("ix__teacher_product__teacher_id"), table_name="teacher_product")
    op.drop_index(op.f("ix__teacher_product__product_id"), table_name="teacher_product")
    op.drop_table("teacher_product")
    op.drop_index(op.f("ix__offer__product_id"), table_name="offer")
    op.drop_index(op.f("ix__offer__cohort"), table_name="offer")
    op.drop_table("offer")
    op.drop_index(op.f("ix__flow_product__soho_id"), table_name="flow_product")
    op.drop_index(op.f("ix__flow_product__product_id"), table_name="flow_product")
    op.drop_index(op.f("ix__flow_product__flow_id"), table_name="flow_product")
    op.drop_table("flow_product")
    op.drop_index(
        op.f("ix__verified_work_file__subject_id"), table_name="verified_work_file"
    )
    op.drop_index(
        op.f("ix__verified_work_file__student_id"), table_name="verified_work_file"
    )
    op.drop_index(
        op.f("ix__verified_work_file__file_id"), table_name="verified_work_file"
    )
    op.drop_table("verified_work_file")
    op.drop_table("soho")
    op.drop_table("reviewer")
    op.drop_index(op.f("ix__product__subject_id"), table_name="product")
    op.drop_index(op.f("ix__product__start_date"), table_name="product")
    op.drop_index(op.f("ix__product__product_group_id"), table_name="product")
    op.drop_index(op.f("ix__product__name"), table_name="product")
    op.drop_index(op.f("ix__product__end_date"), table_name="product")
    op.drop_table("product")
    op.drop_table("distribution")
    op.drop_index(op.f("ix__user__username"), table_name="user")
    op.drop_table("user")
    op.drop_index(op.f("ix__teacher__vk_id"), table_name="teacher")
    op.drop_table("teacher")
    op.drop_index(op.f("ix__subject__name"), table_name="subject")
    op.drop_table("subject")
    op.drop_table("student")
    op.drop_index(op.f("ix__setting__key"), table_name="setting")
    op.drop_table("setting")
    op.drop_index(op.f("ix__product_group__name"), table_name="product_group")
    op.drop_index(op.f("ix__product_group__eng_name"), table_name="product_group")
    op.drop_table("product_group")
    op.drop_table("flow")
