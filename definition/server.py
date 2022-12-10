import typing

import websockets.legacy.server


Connection = typing.TypeVar("Connection", bound=websockets.legacy.server.WebSocketServerProtocol)


class Server(typing.Protocol):
    async def start(
        self,
        handler: typing.Callable[[Connection], typing.Awaitable[None]],
    ) -> None:
        ...

    def stop(
        self,
        exception: typing.Optional[Exception] = None,
    ) -> None:
        ...
