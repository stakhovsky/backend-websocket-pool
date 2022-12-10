import asyncio
import logging
import typing

import definition.storage.expected_solutions_storage


class _Item(typing.NamedTuple):
    height: definition.storage.expected_solutions_storage.Height
    target: definition.storage.expected_solutions_storage.Target
    created_at: float


class Storage(definition.storage.expected_solutions_storage.Storage):
    __slots__ = (
        "_storage",
        "_logger",

        "_wait_time_seconds",
        "_cleanup_task",
    )

    def __init__(
        self,
        logger: typing.Union[logging.Logger, logging.LoggerAdapter],
        wait_time_seconds: int = 20 * 60,
    ) -> None:
        self._storage: typing.MutableSequence[_Item] = []
        self._logger = logger

        self._wait_time_seconds = wait_time_seconds
        self._cleanup_task: typing.Optional[asyncio.Task] = None

    def open(self) -> None:
        loop = asyncio.get_event_loop()
        self._cleanup_task = loop.create_task(self._cleanup(
            ttl_seconds=self._wait_time_seconds,
        ))

    async def _cleanup(
        self,
        ttl_seconds: int = 20 * 60,
    ) -> None:
        loop = asyncio.get_event_loop()

        while True:
            try:
                self._storage = [
                    item for item in self._storage
                    if loop.time() - item.created_at < ttl_seconds
                ]
            except Exception as exc:
                self._logger.exception(exc)
            finally:
                await asyncio.sleep(1)

    def wait(
        self,
        height: definition.storage.expected_solutions_storage.Height,
        target: definition.storage.expected_solutions_storage.Target,
    ) -> None:
        loop = asyncio.get_event_loop()
        self._storage.append(_Item(
            created_at=loop.time(),
            height=height,
            target=target,
        ))

    def is_waits(
        self,
        height: definition.storage.expected_solutions_storage.Height,
        target: definition.storage.expected_solutions_storage.Target,
    ) -> bool:
        return next((
            item for item in self._storage
            if (item.height == height) and (item.target <= target)
        ), None) is not None

    def close(self) -> None:
        if self._cleanup_task:
            self._cleanup_task.cancel()
