import logging
import typing

import definition.entity.job


class Error(Exception):
    ...


class Storage(typing.Protocol):
    async def open(self) -> None:
        ...

    async def store(
        self,
        entry: definition.entity.job.JobInput,
    ) -> typing.Tuple[bool, typing.Optional[definition.entity.job.JobStorageMetadata]]:
        ...

    async def mark_stored(
        self,
        entry: definition.entity.job.JobStorageMetadata,
    ) -> bool:
        ...

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        ...
