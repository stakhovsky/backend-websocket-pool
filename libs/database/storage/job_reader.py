import datetime
import logging
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio

import definition.entity.job
import definition.storage.job_reader

import libs.database.tables.job


class Reader(definition.storage.job_reader.Reader):
    __slots__ = (
        '_db_dsn',
        '_db_engine',
    )

    def __init__(
        self,
        db_dsn: str = "postgresql+asyncpg://postgres:postgres@db:5432/postgres",
    ) -> None:
        self._db_dsn = db_dsn
        self._db_engine: typing.Optional[sqlalchemy.ext.asyncio.AsyncEngine] = None

    async def open(self) -> None:
        self._db_engine = sqlalchemy.ext.asyncio.create_async_engine(
            self._db_dsn,
        )

    async def get(
        self,
        **params: typing.Mapping[str, typing.Any],
    ) -> typing.Optional[definition.entity.job.JobStorageMetadata]:
        async with self._db_engine.connect() as connection:
            query = sqlalchemy.select(
                *libs.database.tables.job.job.c,
            )
            for key, value in params.items():
                query.where(
                    getattr(libs.database.tables.job.job.c, key) == value
                )
            result = (await connection.execute(query)).fetchone()
            if result is None:
                return None
            return definition.entity.job.JobStorageMetadata(
                task_id=result.task_id,
                block_height=result.block_height,
                created_at=result.created_at,
            )

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        if self._db_engine:
            try:
                await self._db_engine.dispose()
            except Exception as exc:
                logger.exception(exc)
