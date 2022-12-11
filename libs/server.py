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

    @staticmethod
    async def _complete_all_tasks(
        server,
    ) -> None:
        if server.ws_server.websockets:
            connection_tasks = (
                websocket.handler_task
                for websocket in server.ws_server.websockets
            )
            await asyncio.shield(asyncio.gather(*connection_tasks))

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
            # just to be completely sure that all connections are stopped here
            await asyncio.shield(self._complete_all_tasks(server))

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
