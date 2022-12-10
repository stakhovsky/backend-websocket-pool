import logging
import typing


Data = typing.TypeVar("Data")


class DisconnectError(Exception):
    ...


class Consumer(typing.Protocol):
    async def open(self) -> None:
        ...

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        ...

    async def consume(
        self,
        message_cls: typing.Type[Data],
        handler: typing.Callable[[Data], typing.Awaitable[None]],
        **_,
    ) -> None:
        ...


class ConsumerFactory(typing.Protocol):
    async def spawn(self) -> Consumer:
        ...
