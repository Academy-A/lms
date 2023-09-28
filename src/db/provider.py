from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.product import ProductRepository
from src.db.repositories.soho import SohoRepository
from src.db.repositories.student import StudentRepository
from src.db.repositories.subject import SubjectRepository
from src.db.repositories.teacher import TeacherRepository


class DatabaseProvider:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.product = ProductRepository(session=session)
        self.soho = SohoRepository(session=session)
        self.student = StudentRepository(session=session)
        self.subject = SubjectRepository(session=session)
        self.teacher = TeacherRepository(session=session)
