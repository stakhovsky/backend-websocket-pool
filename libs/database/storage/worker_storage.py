import datetime
import logging
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.dialects.postgresql

import definition.entity.worker
import definition.storage.worker_storage

import libs.attrgetter
import libs.database.tables.worker


class Storage(definition.storage.worker_storage.Storage):
    __slots__ = (
        '_db_dsn',
        '_redis_dsn',
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

    async def store_connect(
        self,
        entry: definition.entity.worker.Worker,
    ) -> definition.entity.worker.WorkerConnection:
        async with self._db_engine.begin() as connection:
            query = sqlalchemy.dialects.postgresql.insert(
                libs.database.tables.worker.worker,
            ).values({
                "ip": entry.ip,
                "address": entry.address,
                "hardware": entry.hardware,
                "hardware_id": entry.hardware_id,
                "caption": entry.caption,
                "connected_at": datetime.datetime.utcnow(),
            }).returning(
                libs.database.tables.worker.worker.c.id,
            )
            result = (await connection.execute(query)).fetchone()
            return definition.entity.worker.WorkerConnection(
                id=result.id,
            )

    async def store_disconnect(
        self,
        entry: definition.entity.worker.WorkerConnection,
    ) -> None:
        async with self._db_engine.begin() as connection:
            query = sqlalchemy.update(
                libs.database.tables.worker.worker,
            ).values({
                "disconnected_at": datetime.datetime.utcnow(),
            }).where(
                libs.database.tables.worker.worker.c.id == entry.id,
            )
            await connection.execute(query)

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        if self._db_engine:
            try:
                await self._db_engine.dispose()
            except Exception as exc:
                logger.exception(exc)
