import logging
import typing

import definition.entity.worker


class Error(Exception):
    ...


class Storage(typing.Protocol):
    async def open(self) -> None:
        ...

    async def store_connect(
        self,
        entry: definition.entity.worker.Worker,
    ) -> definition.entity.worker.WorkerConnection:
        ...

    async def store_disconnect(
        self,
        entry: definition.entity.worker.WorkerConnection,
    ) -> None:
        ...

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        ...
