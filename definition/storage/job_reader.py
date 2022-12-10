import logging
import typing

import definition.entity.job


class Reader(typing.Protocol):
    async def open(self) -> None:
        ...

    async def get(
        self,
        **_,
    ) -> typing.Optional[definition.entity.job.JobStorageMetadata]:
        ...

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        ...
