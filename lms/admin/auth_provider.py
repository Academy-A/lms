# from starlette.requests import Request
# from starlette.responses import Response
# from starlette_admin.auth import AdminUser, AuthProvider
# from starlette_admin.exceptions import FormValidationError, LoginFailed

# from lms.db.repositories.user import UserRepository
# from lms.exceptions import UserNotFoundError
# from lms.utils.password import verify_password


# class AuthenticationProvider(AuthProvider):
#     async def login(
#         self,
#         username: str,
#         password: str,
#         remember_me: bool,
#         request: Request,
#         response: Response,
#     ) -> Response:
#         if len(username) < 8:
#             raise FormValidationError(
#                 {"username": "Username has at least 8 characters"},
#             )
#         if len(password) < 8:
#             raise FormValidationError(
#                 {"password": "Password has at least 8 characters"},
#             )
#         await self.check_user(request=request, username=username, password=password)

#         request.session.update({"username": username})
#         return response
import logging

from pydantic import BaseModel, ConfigDict, ValidationError
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from lms.db.repositories.user import UserRepository
from lms.exceptions import UserNotFoundError
from lms.utils.password import verify_password

log = logging.getLogger(__name__)


class LoginFormModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=8)

    username: str
    password: str


class AuthBackend(AuthenticationBackend):
    _session_factory: async_sessionmaker[AsyncSession]

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        secret_key: str,
    ) -> None:
        super().__init__(secret_key)
        self._session_factory = session_factory

    async def login(self, request: Request) -> bool:
        login_form = await self._parser_login_form(request)
        if login_form is None:
            return False
        async with self._session_factory() as session:
            try:
                user = await UserRepository(session).get_by_username(
                    login_form.username
                )
                if not verify_password(login_form.password, user.password):
                    return False
            except Exception:  # noqa: BLE001
                return False
        request.session["username"] = user.username
        return True

    async def authenticate(self, request: Request) -> bool:
        username = request.session.get("username", None)
        if username is None:
            return False
        async with self._session_factory() as session:
            try:
                await UserRepository(session).get_by_username(username)
            except UserNotFoundError:
                return False
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def _parser_login_form(self, request: Request) -> LoginFormModel | None:
        data = await request.form()
        try:
            return LoginFormModel.model_validate(data)
        except ValidationError as e:
            log.info("Incorrect form data: %s errors: %s", data, e.errors())
        return None
