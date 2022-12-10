import asyncio
import contextlib
import typing

import definition.job_priority_shield


class Shield(definition.job_priority_shield.Shield):
    __slots__ = (
        "_height",
        "_lock",
    )

    def __init__(self) -> None:
        self._height: typing.Optional[int] = None
        self._lock = asyncio.Lock()

    @contextlib.asynccontextmanager
    async def ensure_priority(  # noqa
        self,
        height: definition.job_priority_shield.Height,
    ) -> typing.AsyncIterable[bool]:
        async with self._lock:
            is_more_prior = (self._height is None) or (self._height < height)
            yield is_more_prior

    def store_priority(
        self,
        height: definition.job_priority_shield.Height,
    ) -> None:
        self._height = height
