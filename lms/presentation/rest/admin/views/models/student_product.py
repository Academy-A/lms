from sqlalchemy import Select, String, cast, or_, select
from sqlalchemy.orm import joinedload

from lms.adapters.db.models import Offer, Product, Student, Teacher, TeacherProduct
from lms.adapters.db.models import StudentProduct as StudentProduct
from lms.presentation.rest.admin.utils import format_datetime_field
from lms.presentation.rest.admin.views.base import AdminCategories, BaseModelView


class StudentProductModelView(BaseModelView, model=StudentProduct):
    category = AdminCategories.MODELS
    column_list = [
        StudentProduct.id,
        StudentProduct.student,
        StudentProduct.product,
        StudentProduct.teacher_product,
        StudentProduct.expulsion_at,
        StudentProduct.created_at,
        StudentProduct.updated_at,
    ]
    column_sortable_list = [
        StudentProduct.id,
        StudentProduct.expulsion_at,
        StudentProduct.created_at,
        StudentProduct.updated_at,
    ]
    column_default_sort = "id"
    column_formatters = {
        StudentProduct.created_at: format_datetime_field,
        StudentProduct.updated_at: format_datetime_field,
        StudentProduct.expulsion_at: format_datetime_field,
    }

    column_searchable_list = [
        "student.name",
        "offer.name",
        "product.name",
    ]
    column_details_list = [
        StudentProduct.id,
        StudentProduct.student,
        StudentProduct.product,
        StudentProduct.teacher_product,
        StudentProduct.offer,
        StudentProduct.flow,
        StudentProduct.cohort,
        StudentProduct.teacher_grade,
        StudentProduct.teacher_graded_at,
        StudentProduct.expulsion_at,
        StudentProduct.created_at,
        StudentProduct.updated_at,
    ]
    column_formatters_detail = {
        StudentProduct.teacher_graded_at: format_datetime_field,
        StudentProduct.expulsion_at: format_datetime_field,
        StudentProduct.created_at: format_datetime_field,
        StudentProduct.updated_at: format_datetime_field,
    }
    form_columns = [
        StudentProduct.student,
        StudentProduct.product,
        StudentProduct.teacher_product,
        StudentProduct.offer,
        StudentProduct.flow,
        StudentProduct.teacher_type,
        StudentProduct.cohort,
        StudentProduct.teacher_grade,
        StudentProduct.teacher_graded_at,
        StudentProduct.expulsion_at,
    ]
    column_export_list = [
        StudentProduct.id,
        "student.name",
        "student.vk_id",
        "teacher_product.teacher.name",
        "teacher_product.teacher.vk_id",
        "offer.name",
        StudentProduct.expulsion_at,
    ]

    def search_query(self, stmt: Select, term: str) -> Select:
        return (
            select(StudentProduct)
            .join(Student, Student.id == StudentProduct.student_id)
            .join(Product, Product.id == StudentProduct.product_id)
            .join(Offer, Offer.id == StudentProduct.offer_id)
            .join(
                TeacherProduct,
                TeacherProduct.id == StudentProduct.teacher_product_id,
                isouter=True,
            )
            .join(Teacher, Teacher.id == TeacherProduct.teacher_id)
            .options(
                joinedload(StudentProduct.student),
                joinedload(StudentProduct.teacher_product),
                joinedload(StudentProduct.teacher_product).joinedload(
                    TeacherProduct.teacher
                ),
                joinedload(StudentProduct.offer),
                joinedload(StudentProduct.product),
            )
        ).where(
            or_(
                Student.name.ilike(f"%{term}%"),
                Teacher.name.ilike(f"%{term}%"),
                Offer.name.ilike(f"%{term}%"),
                Teacher.name.ilike(f"%{term}%"),
                cast(StudentProduct.teacher_type, String).ilike(f"%{term}%"),
            )
        )
