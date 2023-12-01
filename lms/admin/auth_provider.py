from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from lms.db.repositories.user import UserRepository
from lms.exceptions import UserNotFoundError
from lms.services.utils import verify_password


class AuthenticationProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 8:
            raise FormValidationError(
                {"username": "Username has at least 8 characters"},
            )
        if len(password) < 8:
            raise FormValidationError(
                {"password": "Password has at least 8 characters"},
            )
        await self.check_user(request=request, username=username, password=password)

        request.session.update({"username": username})
        return response

    async def check_user(self, request: Request, username: str, password: str) -> None:
        user = await UserRepository(request.state.session).get_by_username(username)
        try:
            if verify_password(password, user.password):
                return
        except Exception:
            pass
        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request: Request) -> bool:
        username = request.session.get("username", None)
        if not username:
            return False
        try:
            user = await UserRepository(request.state.session).get_by_username(username)
        except UserNotFoundError:
            return False
        request.state.user = user
        return True

    def get_admin_user(self, request: Request) -> AdminUser | None:
        user = request.state.user
        return AdminUser(username=user.username)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
