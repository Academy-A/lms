from alembic.autogenerate import compare_metadata
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, MetaData, pool, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    async_engine_from_config,
    create_async_engine,
)

TABLES_FOR_TRUNCATE = (
    "flow",
    "flow_product",
    "offer",
    "product",
    "product_group",
    "reviewer",
    "setting",
    "soho",
    "student",
    "student_product",
    "subject",
    "teacher",
    "teacher_assignment",
    "teacher_product",
    "teacher_product_flow",
    "verified_work_file",
)


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
                _do_run_migrations,
                target_metadata=target_metadata,
                context=context,
            )


async def prepare_new_database(base_pg_dsn: str, new_database: str) -> None:
    """Using default postgres database for creating new test db"""
    engine = create_async_engine(base_pg_dsn)
    async with engine.begin() as conn:
        if await _database_exists(conn, new_database):
            await _drop_database(conn, new_database)
        await _create_database(conn, new_database)
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


def get_diff_db_metadata(connection: Connection, metadata: MetaData):
    migration_ctx = MigrationContext.configure(connection)
    return compare_metadata(context=migration_ctx, metadata=metadata)


async def clear_db(engine: AsyncEngine) -> None:
    """Truncate tables on each test"""
    tables = ", ".join(TABLES_FOR_TRUNCATE)
    sql = f"TRUNCATE TABLE {tables} CASCADE"
    async with engine.connect() as conn:
        await conn.execute(text(sql))
        await conn.commit()
