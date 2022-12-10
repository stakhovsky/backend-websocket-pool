import asyncio
import typing

import websockets

import definition.server
import libs.asyncio


class Server(definition.server.Server):
    __slots__ = (
        "_port",
        
        "_stop_marker",
    )

    def __init__(
        self,
        port: int = 8000,
    ) -> None:
        self._port = port

        self._stop_marker: typing.Optional[asyncio.Future] = None

    async def start(
        self,
        handler: typing.Callable[[definition.server.Connection], typing.Awaitable[None]],
    ) -> None:
        self._stop_marker = libs.asyncio.stop_marker()

        server = websockets.serve(
            handler,
            host="",
            port=self._port,
        )
        try:
            async with server:
                await self._stop_marker
        finally:
            if server.ws_server.websockets:
                await asyncio.gather(*(
                    websocket.handler_task for websocket in server.ws_server.websockets
                ))

    def stop(
        self,
        exception: typing.Optional[Exception] = None,
    ) -> None:
        if self._stop_marker is None:
            return

        if self._stop_marker.done():
            return

        if exception is not None:
            self._stop_marker.set_exception(exception)
            return

        self._stop_marker.set_result(None)
