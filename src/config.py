from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Insperia LMS"
    DEBUG: bool = True

    SECRET_KEY: str
    SECURITY_ALGORITHM: str = "HS256"

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    SOHO_API_TOKEN: str

    def build_db_connection_uri(
        self,
        *,
        driver: str | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> str:
        return "postgresql+{}://{}:{}@{}:{}/{}".format(
            driver or "asyncpg",
            user or self.POSTGRES_USER,
            password or self.POSTGRES_PASSWORD.get_secret_value(),
            host or self.POSTGRES_HOST,
            port or self.POSTGRES_PORT,
            database or self.POSTGRES_DB,
        )

    def build_rabbitmq_connection_url(
        self,
        *,
        driver: str | None = None,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> str:
        return "{}://{}:{}@{}:{}//".format(
            driver or "amqp",
            user or self.RABBITMQ_USER,
            password or self.RABBITMQ_PASSWORD,
            host or self.RABBITMQ_HOST,
            port or self.RABBITMQ_PORT,
        )
