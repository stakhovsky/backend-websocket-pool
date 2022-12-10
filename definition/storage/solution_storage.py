import logging
import typing

import definition.entity.solution


class Error(Exception):
    ...


class Storage(typing.Protocol):
    async def open(self) -> None:
        ...

    async def store(
        self,
        entry: definition.entity.solution.SolutionInput,
    ) -> typing.Tuple[bool, typing.Optional[definition.entity.solution.SolutionStorageData]]:
        ...

    async def mark_stored(
        self,
        entry: definition.entity.solution.SolutionStorageData,
    ) -> bool:
        ...

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        ...
