import logging
import typing


Message = typing.TypeVar("Message")


class Producer(typing.Protocol):
    async def open(self) -> None:
        ...

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        ...

    async def produce(
        self,
        message: Message,
    ) -> None:
        ...
