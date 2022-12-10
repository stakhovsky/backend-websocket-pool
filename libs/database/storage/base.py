import datetime
import logging
import typing

import aioredis
import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.dialects.postgresql

import libs.attrgetter


Entry = typing.TypeVar("Entry")


class StoredEntry(typing.Protocol):
    created_at: datetime.datetime


class Storage:
    table: sqlalchemy.Table
    index_elements: typing.Sequence[str]
    bypass_column_name: str
    stored_entry_dedup_key: str
    dedup_prefix: str
    exception_class: typing.Type[Exception]

    __slots__ = (
        '_db_dsn',
        '_redis_dsn',
        '_db_engine',
        '_redis_connection',
        '_record_ttl_seconds',
    )

    def __init__(
        self,
        db_dsn: str = "postgresql+asyncpg://postgres:postgres@db:5432/postgres",
        redis_dsn: str = "redis://redis:6379/",
        record_ttl_seconds: int = 60 * 60,
    ) -> None:
        self._db_dsn = db_dsn
        self._redis_dsn = redis_dsn
        self._db_engine: typing.Optional[sqlalchemy.ext.asyncio.AsyncEngine] = None
        self._redis_connection: typing.Optional[aioredis.Redis] = None
        self._record_ttl_seconds = record_ttl_seconds

    async def open(self) -> None:
        self._db_engine = sqlalchemy.ext.asyncio.create_async_engine(
            self._db_dsn,
        )
        self._redis_connection = aioredis.Redis.from_url(
            url=self._redis_dsn,
        )

    def _prepare_database_values(
        self,
        entry: Entry,
    ) -> dict:
        ...

    def _prepare_result_entry(
        self,
        record,
    ) -> StoredEntry:
        ...

    async def _store_in_db(
        self,
        entry: Entry,
    ) -> StoredEntry:
        async with self._db_engine.begin() as connection:
            query = sqlalchemy.dialects.postgresql.insert(
                self.table,
            ).values(
                self._prepare_database_values(entry),
            )
            query = query.on_conflict_do_update(
                index_elements=self.index_elements,
                set_={
                    self.bypass_column_name: libs.attrgetter.get_value(query.excluded, self.bypass_column_name),
                },
            ).returning(*self.table.c)
            result = await connection.execute(query)
            return self._prepare_result_entry(result.fetchone())

    async def _is_newly_stored(
        self,
        stored_entry: StoredEntry,
    ) -> bool:
        delta = (datetime.datetime.utcnow() - stored_entry.created_at).total_seconds()
        if delta > self._record_ttl_seconds:
            # assume that the record was already processed long time ago
            return True

        key = f"{self.dedup_prefix}{libs.attrgetter.get_value(stored_entry, self.stored_entry_dedup_key)}"
        flag = await self._redis_connection.get(
            name=key,
        )

        return not bool(flag)

    async def store(
        self,
        entry: Entry,
    ) -> typing.Tuple[bool, StoredEntry]:
        try:
            stored_entry = await self._store_in_db(entry)
            is_newly_stored = await self._is_newly_stored(stored_entry)
            return is_newly_stored, stored_entry
        except Exception as exc:
            raise self.exception_class from exc

    async def mark_stored(
        self,
        stored_entry: StoredEntry,
    ) -> bool:
        try:
            key = f"{self.dedup_prefix}{libs.attrgetter.get_value(stored_entry, self.stored_entry_dedup_key)}"
            return bool(await self._redis_connection.set(
                name=key,
                value=1,
                nx=True,
                ex=self._record_ttl_seconds,
            ))
        except Exception as exc:
            raise self.exception_class from exc

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        if self._db_engine:
            try:
                await self._db_engine.dispose()
            except Exception as exc:
                logger.exception(exc)
        if self._redis_connection:
            try:
                await self._redis_connection.close()
            except Exception as exc:
                logger.exception(exc)
