from alembic.autogenerate import compare_metadata
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from sqlalchemy import Connection, text, MetaData, pool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncConnection,
    async_engine_from_config,
)

from src.config import Settings


async def run_async_migrations(
    config: AlembicConfig,
    target_metadata: MetaData,
    revision: str,
) -> None:
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        return script._upgrade_revs(revision, rev)

    with EnvironmentContext(
        config,
        script=script,
        fn=upgrade,
        as_sql=False,
        starting_rev=None,
        destination_rev=revision,
    ) as context:
        engine = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        async with engine.connect() as connection:
            await connection.run_sync(
                _do_run_migrations, target_metadata=target_metadata, context=context
            )


async def prepare_new_database(settings: Settings) -> None:
    """Using default postgres database for creating new test db"""
    connection_url = settings.build_db_connection_uri(database="postgres")

    engine = create_async_engine(connection_url)
    async with engine.begin() as conn:
        if await _database_exists(conn, settings.POSTGRES_DB):
            await _drop_database(conn, settings.POSTGRES_DB)
        await _create_database(conn, settings.POSTGRES_DB)
    await engine.dispose()


async def _database_exists(connection: AsyncConnection, db_name: str) -> bool:
    query = f"SELECT 1 from pg_database where datname='{db_name}'"
    if await connection.scalar(text(query)):
        return True
    return False


async def _create_database(connection: AsyncConnection, db_name: str) -> None:
    await connection.execute(text("commit"))
    query = "CREATE DATABASE {} ENCODING {} TEMPLATE {}".format(
        db_name, "utf8", "template1"
    )
    await connection.execute(text(query))


async def _drop_database(connection: AsyncConnection, db_name: str) -> None:
    await connection.execute(text("commit"))
    await connection.execute(text(f"DROP DATABASE {db_name}"))


def _do_run_migrations(
    connection: Connection,
    target_metadata: MetaData,
    context: EnvironmentContext,
) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()