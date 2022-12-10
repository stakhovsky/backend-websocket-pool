import asyncio
import logging
import random
import typing

import aiormq

import definition.producer

import libs.json
import libs.retry


class Error(Exception):
    ...


class Producer(definition.producer.Producer):
    _channels_count: int = 25
    _connect_retry_attempts: int = 5
    _retry_attempts: int = 3
    _stop_wait_time_seconds: int = 5

    __slots__ = (
        "_address",
        "_user",
        "_password",
        "_exchange",

        "_lock",
        "_connection",
        "_channels",
    )

    def __init__(
        self,
        address: str = "rabbitmq:5672",
        user: str = "rabbitmq",
        password: str = "rabbitmq_password",
        exchange: str = "",
    ) -> None:
        self._address = address
        self._user = user
        self._password = password
        self._exchange = exchange

        self._lock = asyncio.Lock()
        self._connection: typing.Optional[aiormq.Connection] = None
        self._channels: typing.MutableSequence[aiormq.Channel] = []

    @libs.retry.retry(
        attempts=_connect_retry_attempts,
    )
    async def open(self) -> None:
        self._connection = await aiormq.connect(
            f"amqp://{self._user}:{self._password}@{self._address}//",
        )
        self._channels = []

    async def close(
        self,
        logger: typing.Optional[typing.Union[logging.Logger, logging.LoggerAdapter]] = None,
    ) -> None:
        for src in (*self._channels, self._connection):
            try:
                await src.close(timeout=self._stop_wait_time_seconds)
            except Exception as e:
                if not isinstance(e, asyncio.TimeoutError):
                    if logger is not None:
                        logger.exception(e)

    async def _get_channel(self) -> aiormq.Channel:
        if len(self._channels) < self._channels_count:
            async with self._lock:
                if len(self._channels) < self._channels_count:
                    self._channels.append(await self._connection.channel())  # noqa
        return random.choice(self._channels)

    @libs.retry.retry(
        attempts=_retry_attempts,
    )
    async def produce(
        self,
        message: definition.producer.Message,
    ) -> None:
        if not isinstance(message, bytes):
            message = libs.json.dumps(message)

        channel = await self._get_channel()
        await channel.basic_publish(
            exchange=self._exchange,
            body=message,
        )
