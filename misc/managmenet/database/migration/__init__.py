import os
import typing

import alembic
import alembic.command
import alembic.config
import sqlalchemy


_SCRIPT = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))


def _normalize_migrations_dir(
    migrations_dir: typing.Union[str, typing.Any],
) -> str:
    if not isinstance(migrations_dir, str):
        if not hasattr(migrations_dir, "__file__"):
            raise EnvironmentError("Could not determine migrations storage")
        migrations_dir = os.path.abspath(os.path.dirname(os.path.abspath(migrations_dir.__file__)))
    return migrations_dir


def _get_config(
    db_dsn: str,
    metadata: sqlalchemy.MetaData,
    migrations_dir: str,
    version_table: str = "versions",
) -> alembic.config.Config:
    config = alembic.config.Config(
        attributes=dict(
            metadata=metadata,
            migrations_dir=migrations_dir,
            version_table=version_table,
        ),
    )

    config.set_main_option(
        name="script_location",
        value=_SCRIPT,
    )
    config.set_main_option(
        name="file_template",
        value="%%(year)d_%%(month).2d_%%(day).2d_%%(rev)s_%%(slug)s",
    )
    config.set_main_option(
        name="version_locations",
        value=migrations_dir,
    )
    config.set_main_option(
        name="sqlalchemy.url",
        value=db_dsn,
    )

    return config


def make_migrations(
    db_dsn: str,
    metadata: sqlalchemy.MetaData,
    migrations_dir: typing.Union[str, typing.Any],
    message: str = "Initial",
    version_table: str = "versions",
    autogenerate: bool = True,
) -> None:
    migrations_dir = _normalize_migrations_dir(migrations_dir)

    config = _get_config(
        db_dsn=db_dsn,
        metadata=metadata,
        migrations_dir=migrations_dir,
        version_table=version_table,
    )

    alembic.command.revision(
        config,
        version_path=migrations_dir,
        message=message,
        autogenerate=autogenerate,
    )


def migrate(
    db_dsn: str,
    metadata: sqlalchemy.MetaData,
    migrations_dir: typing.Union[str, typing.Any],
    version_table: str = "versions",
    version: str = "head",
) -> None:
    migrations_dir = _normalize_migrations_dir(migrations_dir)

    config = _get_config(
        db_dsn=db_dsn,
        metadata=metadata,
        migrations_dir=migrations_dir,
        version_table=version_table,
    )

    alembic.command.upgrade(
        config,
        revision=version,
    )


def make_and_migrate(
    db_dsn: str,
    metadata: sqlalchemy.MetaData,
    migrations_dir: typing.Union[str, typing.Any],
    message: str = "Initial",
    version_table: str = "versions",
) -> None:
    make_migrations(
        message=message,
        db_dsn=db_dsn,
        metadata=metadata,
        migrations_dir=migrations_dir,
        version_table=version_table,
        autogenerate=True,
    )
    migrate(
        db_dsn=db_dsn,
        metadata=metadata,
        migrations_dir=migrations_dir,
        version_table=version_table,
        version="head",
    )
